from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('comenzar-grabacion-todas/', views.comenzar_grabacion_todas,
         name='comenzar_grabacion_todas'),
    path('detener-grabacion-todas/',  views.detener_grabacion_todas,
         name='detener_grabacion_todas'),
     path('visualizacion', views.visualizacion,name="visualizacion"),
     path('operacion', views.operacion,name="operacion"),
     path('comenzar-grabacion/<int:cam_id>/', views.comenzar_grabacion_individual, name='comenzar_grabacion_individual'),
     path('detener-grabacion/<int:cam_id>/', views.detener_grabacion_individual, name='detener_grabacion_individual'),
     path("grabaciones/", views.lista_grabaciones, name="lista_grabaciones"),
]
