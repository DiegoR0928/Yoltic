from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from unittest.mock import patch, MagicMock

class ViewsTestCase(TestCase):
    def test_operacion_view(self):
        response = self.client.get(reverse('operacion'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'comando.html')

    def test_visualizacion_view(self):
        with patch('front.views.init_pipelines'):
            response = self.client.get(reverse('visualizacion'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'visualizacion.html')

    def test_lista_grabaciones_view(self):
        response = self.client.get(reverse('lista_grabaciones'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lista_videos.html')

    def test_comenzar_grabacion_todas(self):
        mock_pipeline = MagicMock()
        mock_pipeline.start.return_value = True
        with patch('front.views.recording_pipelines', {
            1: mock_pipeline,
            2: mock_pipeline,
            3: mock_pipeline,
        }):
            response = self.client.post(reverse('comenzar_grabacion_todas'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')

    def test_detener_grabacion_todas(self):
        mock_pipeline = MagicMock()
        mock_pipeline.stop.return_value = None
        with patch('front.views.recording_pipelines', {
            1: mock_pipeline,
            2: mock_pipeline,
            3: mock_pipeline,
        }), patch('front.views.guardar_video_en_bd'):
            response = self.client.post(reverse('detener_grabacion_todas'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')

    def test_comenzar_grabacion_individual_valida(self):
        mock_pipeline = MagicMock()
        mock_pipeline.start.return_value = True
        with patch('front.views.recording_pipelines', {
            1: mock_pipeline,
        }):
            response = self.client.post(reverse('comenzar_grabacion_individual', args=['1']))
        self.assertEqual(response.status_code, 200)

    def test_detener_grabacion_individual_valida(self):
        mock_pipeline = MagicMock()
        mock_pipeline.stop.return_value = None
        with patch('front.views.recording_pipelines', {
            1: mock_pipeline,
        }), patch('front.views.guardar_video_en_bd'):
            response = self.client.post(reverse('detener_grabacion_individual', args=['1']))
        self.assertEqual(response.status_code, 200)

    def test_comenzar_grabacion_individual_invalida(self):
        # No se hace patch, así que se simula una cámara inválida
        response = self.client.post(reverse('comenzar_grabacion_individual', args=['99']))
        self.assertEqual(response.status_code, 404)

