import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path
from blog.consumers import BlogConsumer  # adjust import path based on your app name

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')  # change to your project name

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                path('ws/blog/<int:blog_id>/', BlogConsumer.as_asgi()),
            ])
        )
    ),
})