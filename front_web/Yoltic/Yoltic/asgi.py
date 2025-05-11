import os
import asyncio
import logging
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.middleware import BaseMiddleware
from django.urls import path, re_path
from front.consumers import JoystickConsumer, MjpegStreamConsumer, MjpegStreamConsumer2

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Yoltic.settings')
django_asgi_app = get_asgi_application()

logger = logging.getLogger(__name__)

class MJPEGStreamMiddleware(BaseMiddleware):
    """Middleware to handle MJPEG stream specific requirements"""
    async def __call__(self, scope, receive, send):
        if scope.get('path', '').startswith('/mjpeg'):
            # Set stream-specific headers
            scope['headers'].extend([
                (b'Cache-Control', b'no-cache, no-store, must-revalidate'),
                (b'Pragma', b'no-cache'),
                (b'Expires', b'0'),
            ])
            
            # Add cleanup handling
            try:
                return await asyncio.wait_for(
                    super().__call__(scope, receive, send),
                    timeout=30.0  # 30-second timeout for streams
                )
            except asyncio.TimeoutError:
                logger.info(f"MJPEG stream timeout: {scope['path']}")
                await send({'type': 'http.response.close'})
                return
        
        return await super().__call__(scope, receive, send)

class ConnectionCleanupMiddleware(BaseMiddleware):
    """Ensure proper resource cleanup for all connections"""
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
            ])
        )
    ),
})
