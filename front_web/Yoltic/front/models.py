from django.db import models

class Video(models.Model):
    cam_id = models.CharField(max_length=50)  
    nombreArchivo = models.CharField(max_length=255)
    ruta = models.CharField(max_length=255)  
    fechaGrabacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.cam_id} - {self.nombreArchivo}"
