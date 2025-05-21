# app/routing.py
from django.urls import re_path
from . import consumers
from .consumers import MjpegStreamConsumer, MjpegStreamConsumer2, MjpegStreamConsumer3
from django.urls import path

websocket_urlpatterns = [
     path('mjpeg1/', MjpegStreamConsumer.as_asgi(), {'camera_id': 1}),  # Aquí se registra la URL
     path('mjpeg2/', MjpegStreamConsumer2.as_asgi(), {'camera_id': 2}),  # Aquí se registra la URL
     path('mjpeg3/', MjpegStreamConsumer3.as_asgi(), {'camera_id': 3}),  # Aquí se registra la URL
     re_path(r'ws/joystick/$', consumers.JoystickConsumer.as_asgi()),
]
