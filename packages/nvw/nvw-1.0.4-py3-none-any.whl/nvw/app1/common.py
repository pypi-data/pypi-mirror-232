from collections import namedtuple


_Settings = namedtuple('Settings', [
    'websocket_path',
    'rest_api_user',
    'rest_api_password',
    'rest_api_path_base',
    'rest_api_param_path',
    'rest_api_tpl_path',
    'rest_api_config_path',
    'rest_api_command_path',
    'rest_api_report_path',
    'rest_api_reportentry_path',
])

settings = _Settings(
    'status/',
    'admin',
    'admin',
    'api/',
    'param',
    'template',
    'config',
    'command',
    'report',
    'reportentry',
)
