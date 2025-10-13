from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/target/(?P<client_id>\w+)/$', consumers.Consumers.as_asgi()),  # ws://域名/ws/target/abc123/
]
