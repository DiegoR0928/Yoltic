# app/routing.py
from django.urls import re_path
from . import consumers
from .consumers import MjpegStreamConsumer, MjpegStreamConsumer2
from django.urls import path

websocket_urlpatterns = [
     path('mjpeg1/', MjpegStreamConsumer.as_asgi()),  # Aquí se registra la URL
     path('mjpeg2/', MjpegStreamConsumer2.as_asgi()),  # Aquí se registra la URL
     re_path(r'ws/joystick/$', consumers.JoystickConsumer.as_asgi()),
]
