import os
import asyncio
import logging
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.middleware import BaseMiddleware
from django.urls import path, re_path
from front.consumers import (
    JoystickConsumer,
    MjpegStreamConsumer,
    MjpegStreamConsumer2,
    MjpegStreamConsumer3,
    MonitoreoConsumer,
)

# Establece la variable de entorno para la configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Yoltic.settings')

# Obtiene la aplicación ASGI de Django para manejar peticiones HTTP normales
django_asgi_app = get_asgi_application()

logger = logging.getLogger(__name__)


class MJPEGStreamMiddleware(BaseMiddleware):
    """
    Middleware personalizado para manejar
    requisitos específicos de streams MJPEG.

    - Añade headers HTTP para evitar caching en streams MJPEG.
    - Implementa un timeout de 30 segundos para
    la conexión, para evitar bloqueos.
    - En caso de timeout, cierra la conexión limpiamente.
    """

    async def __call__(self, scope, receive, send):
        if scope.get('path', '').startswith('/mjpeg'):
            # Añade headers para deshabilitar cache
            scope['headers'].extend([
                (b'Cache-Control', b'no-cache, no-store, must-revalidate'),
                (b'Pragma', b'no-cache'),
                (b'Expires', b'0'),
            ])

            try:
                # Llama al siguiente middleware/consumidor con timeout
                return await asyncio.wait_for(
                    super().__call__(scope, receive, send),
                    timeout=30.0
                )
            except asyncio.TimeoutError:
                logger.info(f"MJPEG stream timeout: {scope['path']}")
                await send({'type': 'http.response.close'})
                return

        return await super().__call__(scope, receive, send)


class ConnectionCleanupMiddleware(BaseMiddleware):
    """
    Middleware para asegurar la limpieza correcta de
    recursos en todas las conexiones.
    """

    async def __call__(self, scope, receive, send):
        try:
            return await super().__call__(scope, receive, send)
        except asyncio.CancelledError:
            logger.info(f"Connection cancelled: {scope['path']}")
            raise
        except Exception as e:
            logger.error(f"Connection error: {e}")
            raise


application = ProtocolTypeRouter({
    "http": AuthMiddlewareStack(
        ConnectionCleanupMiddleware(
            MJPEGStreamMiddleware(
                URLRouter([
                    path("mjpeg1/", MjpegStreamConsumer.as_asgi()),
                    path("mjpeg2/", MjpegStreamConsumer2.as_asgi()),
                    path("mjpeg3/", MjpegStreamConsumer3.as_asgi()),
                    re_path(r"^static/", django_asgi_app),
                    re_path(r"", django_asgi_app),
                ])
            )
        )
    ),
    "websocket": AuthMiddlewareStack(
        ConnectionCleanupMiddleware(
            URLRouter([
                path("ws/joystick/", JoystickConsumer.as_asgi()),
                path("ws/monitoreo/", MonitoreoConsumer.as_asgi()),
            ])
        )
    ),
})
