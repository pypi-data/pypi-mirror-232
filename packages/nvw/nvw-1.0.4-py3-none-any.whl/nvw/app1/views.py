from django.shortcuts import get_object_or_404
from django.http import FileResponse, HttpResponse
from django.conf import settings

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import ConfigTemplate, EnvironmentParameter, Report, ReportEntry
from .serializers import ConfigTemplateSerializer, ConfigTextSerializer, EnvironmentParameterSerializer, ReportEntrySerializer, ReportSerializer

import grpc
from .protobuf import device_pb2, device_pb2_grpc
import markdown
from jinja2 import Template

import pathlib
import os
import sys
import json
import subprocess
import zipfile
from io import StringIO
import re
from urllib.parse import quote as urlquote

invalid_filename_char_regex = re.compile(r'[\\/:*?"<>|]')


class ReportEntryViewSet(viewsets.ModelViewSet):
    serializer_class = ReportEntrySerializer

    def get_queryset(self):
        limit = self.request.query_params.get('count', 10)
        report_name = self.request.query_params.get('report', False)
        if report_name:
            return ReportEntry.objects.filter(report=report_name).order_by('post_date').reverse()[:limit]
        else:
            return ReportEntry.objects.all()


class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer

    def get_queryset(self):
        env_name = self.request.query_params.get('env_name', False)
        if env_name:
            return Report.objects.filter(env_name=env_name)
        else:
            return Report.objects.all()

    def get_object(self):
        qs = self.get_queryset()
        obj = get_object_or_404(qs, report_name=self.kwargs['pk'])
        return obj

    @action(detail=True, methods=['get', ])
    def download(self, request, pk=None):
        report = Report.objects.get(report_name=pk)
        entries = ReportEntry.objects.filter(
            report=report).order_by('post_date')
        httpresponse = HttpResponse(content_type='application/zip')
        output_zip = zipfile.ZipFile(httpresponse, 'w')
        html_file = StringIO()
        html_file.write('''<!DOCTYPE html>
<meta charset="utf-8">
<title>Report: %s</title>
<style>
body {
  max-width: 1080px;
  margin: auto;
}
p {
  font-size: 16px;
}
pre.device {
  font-size: 12px;
  background-color: seashell;
}
.timestamp {
  text-align: right;
  font-size: 8px;
  color: gray;
}
figure {
  margin-bottom: 72px;
}
figcaption {
  text-align: center;
  font-size: 12px;
}
summary {
    padding: 1em;
    border: 2px solid gray;
    background-color: white;
    cursor: pointer;
}
details[open] {
    background-color: seashell;
}
button.close {
    position: sticky;
    top: 5em;
    margin: auto;
    display: block;
    opacity:0.5;
}
</style>
''' % str(report.report_name))
        for entry in entries:
            if entry.entry_type.type_name == 'user-input-markdown':
                template = f'''{markdown.markdown(entry.content_text)}<div class="timestamp">{entry.post_date}</div>'''
            elif entry.entry_type.type_name == 'device-update-config':
                template = f'''
<details>
<summary>Change configuration of <code>{json.loads(entry.meta_data)['target_host']}</code></summary>
<button class="close" onclick="this.parentNode.open=false;">Close</button>
<figure>
  <pre class="device">{entry.content_text}</pre>
</figure>
</details>
<div class="timestamp">{entry.post_date}</div>
'''
            elif entry.entry_type.type_name == 'user-submit-config-template':
                template = f'''
<details>
<summary>Submit configuration template to <code>{[ dev['name'] for dev in json.loads(entry.meta_data)['target_hosts']]}</code></summary>
<button class="close" onclick="this.parentNode.open=false;">Close</button>
<figure>
  <pre class="device">{entry.content_text}</pre>
</figure>
</details>
<div class="timestamp">{entry.post_date}</div>
'''
            elif entry.entry_type.type_name == 'user-submit-config-parameter':
                template = f'''
<details>
<summary>Submit configuration parameter</summary>
<button class="close" onclick="this.parentNode.open=false;">Close</button>
<figure>
  <pre class="device">{entry.content_text}</pre>
</figure>
</details>
<div class="timestamp">{entry.post_date}</div>
'''
            elif entry.entry_type.type_name == 'device-show-config':
                template = f'''
<details>
<summary>Show configuration of <code>{json.loads(entry.meta_data)['target_host']}</code></summary>
<button class="close" onclick="this.parentNode.open=false;">Close</button>
<figure>
  <pre class="device">{entry.content_text}</pre>
</figure>
</details>
<div class="timestamp">{entry.post_date}</div>
'''
            elif entry.entry_type.type_name == 'device-execute-command':
                template = f'''
<details>
<summary>Execute command on <code>{json.loads(entry.meta_data)['target_host']} &gt; {json.loads(entry.meta_data)['command']}</code></summary>
<button class="close" onclick="this.parentNode.open=false;">Close</button>
<figure>
  <pre class="device">{entry.content_text}</pre>
</figure>
</details>
<div class="timestamp">{entry.post_date}</div>
'''
            elif entry.entry_type.type_name == 'user-start-packet-capture':
                template = f'''<p>capture start:  <a href="./{entry.content_file.name}">{entry.content_file.name}</a> (at {entry.post_date})</p>'''
                output_zip.write(entry.content_file.path,
                                 arcname=entry.content_file.name)
            elif entry.entry_type.type_name == 'user-stop-packet-capture':
                template = f'''<p>capture stop: <a href="./{json.loads(entry.meta_data)['filename']}">{json.loads(entry.meta_data)['filename']}</a> (at {entry.post_date})</p>'''
            html_file.write(template)
        html_file.seek(0)
        output_zip.writestr('index.html', html_file.read())
        output_zip.writestr('topology.json', subprocess.run(
            ['terraform', 'output', '-json'], capture_output=True,
            text=True, cwd=f'{os.environ["_NVIEW_ENVDIR"]}/{report.env_name}').stdout)
        download_filename = f'{urlquote(invalid_filename_char_regex.sub("_", str(report.report_name)).encode("utf-8"))}.zip'
        httpresponse[
            'Content-Disposition'] = f"attachment; filename*=utf-8''{download_filename}"
        return httpresponse


class EnvironmentParameterViewSet(viewsets.ModelViewSet):
    serializer_class = EnvironmentParameterSerializer

    def get_queryset(self):
        env_params = EnvironmentParameter.objects.all()
        env_names_qset = env_params.values('env_name').distinct()
        result = EnvironmentParameter.objects.none()
        for query in env_names_qset:
            result = result | EnvironmentParameter.objects.filter(
                env_name=query['env_name']).order_by('post_date').reverse()[:1]
        return result

    def get_object(self):
        qs = self.get_queryset()
        obj = get_object_or_404(qs, env_name=self.kwargs['pk'])
        return obj


class ConfigTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = ConfigTemplateSerializer

    def get_queryset(self):
        env_params = ConfigTemplate.objects.all()
        env_names_qset = env_params.values('env_name').distinct()
        result = ConfigTemplate.objects.none()
        for query in env_names_qset:
            result = result | ConfigTemplate.objects.filter(
                env_name=query['env_name']).order_by('post_date').reverse()[:1]
        return result

    def get_object(self):
        qs = self.get_queryset()
        obj = get_object_or_404(qs, env_name=self.kwargs['pk'])
        return obj


settings_dir = str(pathlib.Path.home() / '.nview')
sys.path.append(settings_dir)
import settings as nview_settings
device_agents = nview_settings.device_agents


class ConfigTextViewSet(viewsets.ViewSet):

    def retrieve(self, request, pk=None, **kwargs):
        device_name = kwargs['device_name']
        env_name = kwargs['env_name']

        node_info = get_node_info(device_name, env_name)

        device = device_pb2.Device(
            host=device_name, user=node_info['user'], password=node_info['password'])
        device_type = node_info['type']

        with grpc.insecure_channel(device_agents[device_type]) as channel:
            stub = device_pb2_grpc.ConfigStub(channel)
            res = stub.get(device)

        ser = ConfigTextSerializer({
            'device_name': device_name, 'config_text': res.text})
        return Response(ser.data)

    def update(self, request, pk=None, **kwargs):
        device_name = kwargs['device_name']
        env_name = kwargs['env_name']

        node_info = get_node_info(device_name, env_name)

        device = device_pb2.Device(
            host=device_name, user=node_info['user'], password=node_info['password'])
        device_type = node_info['type']

        tpl = ConfigTemplate.objects.last().template_string
        params_json = EnvironmentParameter.objects.last().parameters

        j2_template = Template(tpl)
        params = json.loads(params_json)

        device_params = params['devices'][device_name]
        common_params = params['common']
        all_devices_params = {"devices": params['devices']}
        device_params.update(common_params)
        device_params.update(all_devices_params)
        device_params['_key'] = device_name
        rendered_config = j2_template.render(device_params)

        confreq = device_pb2.ConfigRequest(
            device=device, config_text=device_pb2.ConfigText(text=rendered_config))

        with grpc.insecure_channel(device_agents[device_type]) as channel:
            stub = device_pb2_grpc.ConfigStub(channel)
            res = stub.set(confreq)

        if res.error:
            return Response({
                'error': res.error,
                'error_message': res.error_message.message,
                'output': res.output,
            }, status=400)
        else:
            return Response({
                'error': res.error,
                'error_message': res.error_message.message,
                'output': res.output,
            }, status=200)


class CommandExecutionViewSet(viewsets.ViewSet):
    def create(self, request, pk=None, **kwargs):
        device_name = kwargs['device_name']
        env_name = kwargs['env_name']

        node_info = get_node_info(device_name, env_name)

        device = device_pb2.Device(
            host=device_name, user=node_info['user'], password=node_info['password'])
        device_type = node_info['type']

        commandreq = device_pb2.CommandRequest(
            device=device, command_text=device_pb2.CommandText(text=request.data['command']))

        with grpc.insecure_channel(device_agents[device_type]) as channel:
            stub = device_pb2_grpc.CommandStub(channel)
            res = stub.execute(commandreq)

        if res.error:
            return Response({
                'error': res.error,
                'error_message': res.error_message.message,
                'output': res.output,
            }, status=400)
        else:
            return Response({
                'error': res.error,
                'error_message': res.error_message.message,
                'output': res.output,
            }, status=200)


def get_node_info(device_name, env_name):
    envdir = os.environ['_NVIEW_ENVDIR']
    output_str = subprocess.run(
        ['terraform', 'output', '-json'], capture_output=True, text=True, cwd=f'{envdir}/{env_name}').stdout
    output_json = json.loads(output_str)
    node_info_list = output_json['topology']['value']['nodes']

    node_info = [
        *filter(lambda x: x['name'] == device_name, node_info_list)][0]
    return node_info


def download_view(request, filename):
    file_path = settings.MEDIA_ROOT / filename
    return FileResponse(open(file_path, "rb"), as_attachment=True, filename=filename)
