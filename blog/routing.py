from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/blog/(?P<blog_id>\w+)/$', consumers.BlogConsumer.as_asgi()),
]