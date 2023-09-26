from django.urls import path
from app1.consumers import StatusConsumer
from app1.common import settings as common_settings
import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                [
                    path(f'{common_settings.websocket_path}',
                         StatusConsumer.as_asgi(), name='status'),
                ]
            )
        )
    ),
})
