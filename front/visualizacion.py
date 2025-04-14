import sys
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import Gst

class ventanaVisualizacion(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Visualización de Cámaras")
        self.setGeometry(40, 40, 1200, 600)
        self.setWindowIcon(QIcon('../logo.png'))

        # Layout principal
        layout = QHBoxLayout()

        # Crear etiquetas de visualización
        self.video_widgets = []
        for i in range(3):
            label = QLabel(f"Cámara {i+1}")
            label.setAlignment(Qt.AlignCenter)
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.video_widgets.append(label)
            layout.addWidget(label)

        self.setLayout(layout)

        # Inicializar GStreamer
        Gst.init(None)

        # URIs de los streams RTP de las cámaras
        self.streams = [
            "rtsp://192.168.1.82:8554/cam1",  # Cámara 1
            "rtp://192.168.1.82:10003",  # Cámara 2
            "rtp://192.168.1.82:10004"   # Cámara 3
        ]

        # Inicializar pipelines
        self.pipelines = []
        self.video_sinks = []

        # Crear pipelines para cada cámara
        for idx, stream_uri in enumerate(self.streams):
            # Crear un pipeline para cada cámara
            pipeline = Gst.Pipeline.new(f"pipeline{idx}")
            playbin = Gst.ElementFactory.make("playbin", f"playbin{idx}")
            playbin.set_property("uri", stream_uri)

            # Crear video sink (QVideoWidget)
            videosink = Gst.ElementFactory.make("qt6videosink", None)

            # Asignar el video sink al playbin
            playbin.set_property("video-sink", videosink)

            # Añadir el playbin al pipeline
            pipeline.add(playbin)

            # Guardar el video sink para mostrar el video en la interfaz
            self.video_sinks.append(videosink)

            # Iniciar el pipeline
            pipeline.set_state(Gst.State.PLAYING)

            # Guardar el pipeline en la lista
            self.pipelines.append(pipeline)

        # Timer para actualizar las imágenes
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        # Aquí se puede implementar lógica para actualizar las imágenes si es necesario
        # Actualmente, GStreamer gestiona la visualización automáticamente a través de los sinks.
        pass

    def closeEvent(self, event):
        # Detener todos los pipelines cuando se cierra la ventana
        for pipeline in self.pipelines:
            pipeline.set_state(Gst.State.NULL)
        event.accept()
