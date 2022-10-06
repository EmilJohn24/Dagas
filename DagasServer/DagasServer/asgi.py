"""
ASGI config for DagasServer project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

import relief.routing as routing
asgi_application = get_asgi_application()
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DagasServer.settings')
#
# django.setup()

application = ProtocolTypeRouter(
    {
        "http": asgi_application,
        "https": asgi_application,
        "websocket": AuthMiddlewareStack(
                URLRouter(
                    routing.websocket_urlpatterns
                )
            ),
    }
)

