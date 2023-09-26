import os
import json
import subprocess
import threading
from time import strftime

from channels.generic.websocket import WebsocketConsumer
from django.core.files.base import ContentFile
from django.conf import settings

from .models import ReportEntry, ReportEntryType, Report
from .utils import get_topology_info


class StatusConsumer(WebsocketConsumer):
    def connect(self):

        self.accept()

    def disconnect(self, close_code):
        pass

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        requesttype = text_data_json['request']
        options = text_data_json['option']

        envdir = os.environ['_NVIEW_ENVDIR']
        dumpcmd = os.environ['_NVIEW_DUMPCMD']

        if requesttype == 'topology':
            topology_info = get_topology_info(f'{envdir}/{options["env"]}', options)
            topology_info['topology']['value']['response'] = 'topology'

            self.send(text_data=json.dumps(topology_info['topology']['value']))
        if requesttype == 'capture':
            topology_info = get_topology_info(envdir, options)
            node_name = options["node"]
            node_info_from_json = [
                *filter(lambda x: x['name'] == node_name, topology_info['topology']['value']['nodes'])][0]
            if node_info_from_json['type'] == 'junos':
                node_name = f'{node_name}-pfe'
            output_str = subprocess.run(
                f'virsh domiflist {node_name} | awk \'$3=="{options["bridge"]}"{{print $1}}\'', capture_output=True, text=True, shell=True).stdout
            port = output_str.split('\n')[0]
            myenv = os.environ.copy()
            myenv["LANG"] = "C"
            pcap_filename = strftime(
                f'%Y%m%d-%H%M%S-{node_name}-{options["bridge"]}.pcap')
            report_name = options.get('report', None)
            if report_name is not None:
                empty_file = ContentFile('')
                empty_file.name = pcap_filename
                report_entry = ReportEntry(
                    report=Report.objects.get(report_name=report_name),
                    entry_type=ReportEntryType.objects.get(
                        type_name='user-start-packet-capture'),
                    content_file=empty_file,
                    meta_data=json.dumps({
                        'filename': pcap_filename,
                        'node': node_name,
                        'edge': options["bridge"],
                    }))
                report_entry.save()
            popen = subprocess.Popen([
                'ovs-tcpdump',
                '-i', f'{port}',
                '--mirror-to', f'm{options["bridge"]}',
                '--dump-cmd', f'{dumpcmd}', settings.MEDIA_ROOT / pcap_filename
            ], env=myenv)
            thread1 = threading.Thread(target=pcap_observer,
                                       args=[self, popen, pcap_filename, node_name, options["bridge"], report_name])
            thread1.start()
            self.send(text_data=json.dumps(
                {'response': 'capture', 'state': 'start', 'node': node_name, 'edge': options['bridge']}))

        if requesttype == 'envlist':
            envlist = os.listdir(envdir)
            self.send(text_data=json.dumps(
                {'response': 'envlist', 'list': envlist}))


def pcap_observer(
        websocket: 'StatusConsumer', pipe: 'subprocess.Popen',
        pcap_name: 'str', node_name: 'str', edge_name: 'str', report_name: 'str') -> 'None':
    pipe.wait()
    websocket.send(text_data=json.dumps(
        {'response': 'capture', 'state': 'stop', 'node': node_name, 'edge': edge_name}))
    if report_name is not None:
        report_entry = ReportEntry(
            report=Report.objects.get(report_name=report_name),
            entry_type=ReportEntryType.objects.get(
                type_name='user-stop-packet-capture'),
            meta_data=json.dumps({
                'filename': pcap_name,
                'node': node_name,
                'edge': edge_name,
            }))
        report_entry.save()

