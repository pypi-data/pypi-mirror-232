import shutil
import subprocess
import sys
import pathlib
import json
import os

settings_dir = str(pathlib.Path.home() / '.nview')


def confgen():
    os.makedirs(settings_dir, exist_ok=True)
    shutil.copy(f'{__path__[0]}/settings-template.py', f'{settings_dir}/')


def run():

    sys.path.append(settings_dir)

    try:
        import settings as user_settings
    except:
        print('Failed to load config. \nMissing config dir (~/.nview/settings.py)\n or all contents is commented out?', file=sys.stderr)
        os._exit(1)

    port = user_settings.server_port

    os.environ['_NVIEW_ALLOWED_HOSTS'] = user_settings.allowed_hosts
    os.environ['_NVIEW_ENVDIR'] = user_settings.env_dir
    os.environ['_NVIEW_DUMPCMD'] = user_settings.dump_cmd
    os.environ['_NVIEW_DJANGO_DEBUG'] = user_settings.django_debug
    os.environ['_NVIEW_DJANGO_SECRET'] = user_settings.django_secret
    os.environ['_NVIEW_TOPOLOGY_COMMAND'] = user_settings.topology_command
    if user_settings.xdisplay is not None:
        os.environ['DISPLAY'] = user_settings.xdisplay
    myenv = os.environ.copy()

    from nvw.app1.common import settings as common_settings

    with open(f"{__path__[0]}/app1/static/settings.json", "w") as setting_file:
        setting_file.write(json.dumps({
            "websocket_uri": user_settings.websocket_uri,
            "websocket_path": common_settings.websocket_path,
            "rest_api_user": common_settings.rest_api_user,
            "rest_api_password": common_settings.rest_api_password,
            "rest_api_path_base": common_settings.rest_api_path_base,
            "rest_api_param_path": common_settings.rest_api_param_path,
            "rest_api_tpl_path": common_settings.rest_api_tpl_path,
            "rest_api_config_path": common_settings.rest_api_config_path,
            "rest_api_command_path": common_settings.rest_api_command_path,
            "rest_api_report_path": common_settings.rest_api_report_path,
            "rest_api_reportentry_path": common_settings.rest_api_reportentry_path,
        }))

    subprocess.run(f'{__path__[0]}/manage.py makemigrations', shell=True)
    subprocess.run(f'{__path__[0]}/manage.py migrate', shell=True)
    subprocess.run(
        f'{__path__[0]}/manage.py runserver 0:{port}', shell=True, env=myenv)
