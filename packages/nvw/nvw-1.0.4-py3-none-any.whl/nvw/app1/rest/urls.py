from rest_framework import routers
from django.urls import re_path

from ..common import settings
from ..views import ConfigTemplateViewSet, ConfigTextViewSet, EnvironmentParameterViewSet, ReportViewSet, ReportEntryViewSet, CommandExecutionViewSet


param_path = settings.rest_api_param_path
tpl_path = settings.rest_api_tpl_path
config_path = settings.rest_api_config_path
command_path = settings.rest_api_command_path
report_path = settings.rest_api_report_path
reportentry_path = settings.rest_api_reportentry_path

router = routers.SimpleRouter()
router.register(f'{param_path}', EnvironmentParameterViewSet, basename='param')
router.register(f'{tpl_path}', ConfigTemplateViewSet, basename='template')
router.register(f'{report_path}', ReportViewSet, basename='report')
router.register(f'{reportentry_path}', ReportEntryViewSet,
                basename='reportentry')
#router.register(r'config', ConfigTextViewSet, basename='config')

urlpatterns = [
    re_path(
        r'^' + config_path + r'/(?P<env_name>[^/]+)/(?P<device_name>[^/]+)/', ConfigTextViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
        }), name='config'),
    re_path(
        r'^' + command_path + r'/(?P<env_name>[^/]+)/(?P<device_name>[^/]+)/', CommandExecutionViewSet.as_view({
            'post': 'create',
        }), name='command'),
]
urlpatterns += router.urls
