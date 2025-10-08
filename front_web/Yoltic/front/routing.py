# app/routing.py
from .consumers import (
    MjpegStreamConsumer,
    MjpegStreamConsumer2,
    MjpegStreamConsumer3,
)
from django.urls import path

websocket_urlpatterns = [
    path('mjpeg1/', MjpegStreamConsumer.as_asgi(),
         {'camera_id': 1}),
    path('mjpeg2/', MjpegStreamConsumer2.as_asgi(),
         {'camera_id': 2}),
    path('mjpeg3/', MjpegStreamConsumer3.as_asgi(),
         {'camera_id': 3})
]
