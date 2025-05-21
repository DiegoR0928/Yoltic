import os
from django.shortcuts import render
from django.http import JsonResponse
import traceback
from django.views.decorators.http import require_POST
from django.conf import settings

# Create your views here.
def index(request):
    return render(request, 'index.html')

# En tu views.py o donde manejes las acciones
from .grabacion_pipeline import GrabacionPipeline

# Inicialización de los pipelines de grabación
recording_pipelines = {
    1: GrabacionPipeline(
        rtsp_url="rtsp://192.168.1.74:8554/cam1",
        output_dir=settings.MEDIA_ROOT,
        camera_id=1
    ),
    2: GrabacionPipeline(
        rtsp_url="rtsp://192.168.1.74:8554/cam2",
        output_dir=settings.MEDIA_ROOT,
        camera_id=2
    ),
    3: GrabacionPipeline(
        rtsp_url="rtsp://192.168.1.74:8554/cam3",
        output_dir=settings.MEDIA_ROOT,
        camera_id=3
    )
}

@require_POST
def comenzar_grabacion_todas(request):
    try:
        print("🎬 Iniciando grabación para todas las cámaras")
        results = {}
        for camera_id, pipeline in recording_pipelines.items():
            success = pipeline.start()
            results[camera_id] = "success" if success else "failed"
            print(f"  Cámara {camera_id}: {'✅' if success else '❌'}")
        
        if all(status == "success" for status in results.values()):
            return JsonResponse({
                "status": "success",
                "message": "Grabación iniciada para todas las cámaras",
                "results": results
            })
        else:
            return JsonResponse({
                "status": "partial",
                "message": "Grabación iniciada con algunos errores",
                "results": results
            }, status=207)
            
    except Exception as e:
        print(f"❌ Error al iniciar grabación: {str(e)}")
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)

@require_POST
def detener_grabacion_todas(request):
    try:
        print("🛑 Deteniendo grabación para todas las cámaras")
        results = {}
        for camera_id, pipeline in recording_pipelines.items():
            pipeline.stop()
            results[camera_id] = "stopped"
            print(f"  Cámara {camera_id}: ⏹️")
        
        return JsonResponse({
            "status": "success",
            "message": "Grabación detenida para todas las cámaras",
            "results": results
        })
    except Exception as e:
        print(f"❌ Error al detener grabación: {str(e)}")
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)
