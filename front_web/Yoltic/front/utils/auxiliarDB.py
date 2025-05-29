
import os
from pathlib import Path
from django.conf import settings
from django.utils.timezone import now
from ..models import Video  

def guardar_video_en_bd(pipeline):
    """
    Guarda en la base de datos el archivo de video generado por el pipeline.
    """
    if not pipeline.output_file or not os.path.exists(pipeline.output_file):
        print("⚠️ No se encontró el archivo para guardar en BD.")
        return

    archivo_path = Path(pipeline.output_file)
    relative_path = archivo_path.relative_to(settings.MEDIA_ROOT)

    Video.objects.create(
        cam_id=pipeline.camera_id,
        nombreArchivo=archivo_path.name,
        ruta=str(relative_path),
        fechaGrabacion=now()
    )
    print(f"✅ Video guardado en BD: {archivo_path.name}")
