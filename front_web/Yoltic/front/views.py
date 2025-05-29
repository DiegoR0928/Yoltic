from .utils.auxiliarDB import guardar_video_en_bd
from .grabacion_pipeline import GrabacionPipeline
from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from django.conf import settings
from .iniciarPipelines import init_pipelines
import os

# Create your views here.


def index(request):
    """
    Renderiza la página principal.

    Args:
        request (HttpRequest): Objeto de la petición HTTP.

    Returns:
        HttpResponse: Respuesta con la plantilla 'index.html'.
    """
    return render(request, 'index.html')

def visualizacion(request):
    """
    Renderiza la página de visualizacion 

    Args:
        request (HttpRequest): Objeto de la petición HTTP.

    Returns:
        HttpResponse: Respuesta con la plantilla 'visualización.html'.
    """
    init_pipelines()
    return render(request, 'visualizacion.html')

def operacion(request):
    """
    Renderiza la página de comandos

    Args:
        request (HttpRequest): Objeto de la petición HTTP.

    Returns:
        HttpResponse: Respuesta con la plantilla 'comando.html'.
    """
    return render(request, 'comando.html')


# Inicialización de los pipelines de grabación
recording_pipelines = {
    1: GrabacionPipeline(
        rtsp_url="rtsp://192.168.1.75:8554/cam1",
        output_dir=settings.MEDIA_ROOT,
        camera_id=1
    ),
    2: GrabacionPipeline(
        rtsp_url="rtsp://192.168.1.75:8554/cam2",
        output_dir=settings.MEDIA_ROOT,
        camera_id=2
    ),
    3: GrabacionPipeline(
        rtsp_url="rtsp://192.168.1.75:8554/cam3",
        output_dir=settings.MEDIA_ROOT,
        camera_id=3
    )
}


@require_POST
def comenzar_grabacion_todas(request):
    """
    Inicia la grabación para todas las cámaras configuradas.

    Args:
        request (HttpRequest): Objeto de la petición HTTP (POST).

    Returns:
        JsonResponse: Respuesta JSON con el estado de la operación.
                      - status: 'success' si todas las
                      grabaciones iniciaron correctamente,
                        'partial' si algunas fallaron, o
                        'error' si hubo una excepción.
                      - message: Mensaje descriptivo.
                      - results: Diccionario con estado por cámara.
    """
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
    """
    Detiene la grabación para todas las cámaras configuradas.

    Args:
        request (HttpRequest): Objeto de la petición HTTP (POST).

    Returns:
        JsonResponse: Respuesta JSON indicando el resultado de la detención.
                      - status: 'success' si se detuvo
                      correctamente o 'error' si hubo excepción.
                      - message: Mensaje descriptivo.
                      - results: Diccionario con estado por cámara.
    """
    try:
        print("🛑 Deteniendo grabación para todas las cámaras")
        results = {}
        for camera_id, pipeline in recording_pipelines.items():
            pipeline.stop()
            guardar_video_en_bd(pipeline)
            results[camera_id] = "stopped & saved"
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


@require_POST
def comenzar_grabacion_individual(request, cam_id):
    """
    Inicia la grabación para una cámara específica según su ID.

    Args:
        request (HttpRequest): Objeto de la petición HTTP (POST).
        cam_id (str): ID de la cámara a grabar.

    Returns:
        JsonResponse: Respuesta JSON con el estado de la operación.
    """
    try:
        pipeline = recording_pipelines.get(cam_id)
        if not pipeline:
            raise Http404(f"Cámara con ID '{cam_id}' no encontrada")

        success = pipeline.start()
        status = "success" if success else "failed"
        print(f"🎬 Iniciando grabación cámara {cam_id}: {'✅' if success else '❌'}")

        return JsonResponse({
            "status": status,
            "message": f"Grabación {'iniciada' if success else 'fallida'} para cámara {cam_id}",
            "results": {cam_id: status}
        }, status=200 if success else 500)

    except Exception as e:
        print(f"❌ Error al iniciar grabación cámara {cam_id}: {str(e)}")
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)


@require_POST
def detener_grabacion_individual(request, cam_id):
    """
    Detiene la grabación para una cámara específica según su ID.

    Args:
        request (HttpRequest): Objeto de la petición HTTP (POST).
        cam_id (str): ID de la cámara a detener.

    Returns:
        JsonResponse: Respuesta JSON con el estado de la operación.
    """
    try:
        pipeline = recording_pipelines.get(cam_id)
        if not pipeline:
            raise Http404(f"Cámara con ID '{cam_id}' no encontrada")

        pipeline.stop()
        print(f"🛑 Deteniendo grabación cámara {cam_id}: ⏹️")
        guardar_video_en_bd(pipeline)

        return JsonResponse({
            "status": "success",
            "message": f"Grabación detenida para cámara {cam_id}",
            "results": {cam_id: "stopped"}
        })

    except Exception as e:
        print(f"❌ Error al detener grabación cámara {cam_id}: {str(e)}")
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)
    
def lista_grabaciones(request):
    carpeta_grabaciones = settings.MEDIA_ROOT
    archivos = []

    if os.path.exists(carpeta_grabaciones):
        for nombre_archivo in os.listdir(carpeta_grabaciones):
            if nombre_archivo.endswith(".mp4"):
                archivos.append({
                    "nombre": nombre_archivo,
                    "ruta": settings.MEDIA_URL + nombre_archivo,
                })

    return render(request, "lista_videos.html", {"videos": archivos})