"""
ASGI config for DagasServer project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

import django
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from django.urls import re_path


from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DagasServer.settings')
django.setup()
asgi_application = get_asgi_application()

from relief import consumers

#

application = ProtocolTypeRouter(
    {
        "http": asgi_application,
        "https": asgi_application,
        "websocket":  AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(
                    [
                        re_path(r"^algorithm/$", consumers.AlgorithmConsumer.as_asgi())
                    ]
                )
            )
        ),
    }
)

