from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('comenzar-grabacion-todas/', views.comenzar_grabacion_todas, name='comenzar_grabacion_todas'),
    path('detener-grabacion-todas/',  views.detener_grabacion_todas,  name='detener_grabacion_todas'),
]
