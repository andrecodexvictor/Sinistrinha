from django.urls import re_path
from . import consumers
from .player_consumer import PlayerConsumer

websocket_urlpatterns = [
    re_path(r'^ws/casino/$', consumers.CasinoConsumer.as_asgi()),
    re_path(r'^ws/user/(?P<user_id>\d+)/$', consumers.UserConsumer.as_asgi()),
    re_path(r'^ws/player/(?P<user_id>\d+)/$', PlayerConsumer.as_asgi()),
]
