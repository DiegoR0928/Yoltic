from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # Ruta para el panel de administración de Django
    path('admin/', admin.site.urls),

    # Incluye todas las rutas definidas en front/urls.py
    path('', include('front.urls')),


    path('', include('usuarios.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
