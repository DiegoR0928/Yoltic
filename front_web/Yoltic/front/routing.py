# app/routing.py
from django.urls import re_path
from . import consumers
from .consumers import MjpegStreamConsumer
from django.urls import path

websocket_urlpatterns = [
     path('mjpeg/', MjpegStreamConsumer.as_asgi()),  # Aquí se registra la URL
     re_path(r'ws/joystick/$', consumers.JoystickConsumer.as_asgi()),
]
