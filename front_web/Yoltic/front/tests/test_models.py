from django.test import TestCase
from front.models import Video

class VideoModelTest(TestCase):

    def test_crear_video(self):
        video = Video.objects.create(
            cam_id="1",
            nombreArchivo="video_test.mp4",
            ruta="/videos/video_test.mp4"
        )
        self.assertEqual(video.cam_id, "1")
        self.assertEqual(video.nombreArchivo, "video_test.mp4")
        self.assertEqual(video.ruta, "/videos/video_test.mp4")
        self.assertIsNotNone(video.fechaGrabacion)

    def test_str_method(self):
        video = Video(cam_id="2", nombreArchivo="archivo.mp4", ruta="/videos/archivo.mp4")
        self.assertEqual(str(video), "2 - archivo.mp4")

