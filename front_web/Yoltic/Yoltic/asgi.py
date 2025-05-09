import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path, re_path
from front.consumers import JoystickConsumer, MjpegStreamConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Yoltic.settings')
django_asgi_app = get_asgi_application()  # Incluye WhiteNoise

application = ProtocolTypeRouter({
    "http": URLRouter([
        path("mjpeg/", MjpegStreamConsumer.as_asgi()),  # Ruta especial MJPEG
        re_path(r"^static/", django_asgi_app),  # WhiteNoise maneja /static/
        re_path(r"", django_asgi_app),  # Todas las demás rutas HTTP
    ]),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/joystick/", JoystickConsumer.as_asgi()),
        ])
    ),
})