import sys
import threading
import numpy as np
from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QImage, QPixmap, QIcon
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QHBoxLayout
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

class ventanaVisualizacion(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Visualizacion Yoltic")
        self.setGeometry(100, 100, 1200, 480)
        self.setWindowIcon(QIcon("./logo.png"))

        # Crear layout horizontal para las tres cámaras
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        # Crear tres QLabel (una por cámara)
        self.labels = []
        for i in range(3):
            label = QLabel(f"Esperando video cámara {i+1}...")
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("background-color: black; color: white;")
            self.labels.append(label)
            self.layout.addWidget(label)

        # Inicializar GStreamer
        Gst.init(None)

        # Configurar solo la primera cámara por ahora
        self.pipeline = Gst.parse_launch(
            'rtspsrc location=rtsp://192.168.1.105:8554/cam1 protocols=udp+tcp ! '
            'rtph264depay ! avdec_h264 ! videoconvert ! video/x-raw,format=RGB ! appsink name=sink sync=false max-buffers=1 drop=true'
        )

        self.appsink = self.pipeline.get_by_name("sink")
        self.appsink.set_property("emit-signals", True)
        self.appsink.connect("new-sample", self.on_new_sample)

        # Iniciar el pipeline en un hilo separado
        threading.Thread(target=self._run_pipeline, daemon=True).start()

    def _run_pipeline(self):
        self.pipeline.set_state(Gst.State.PLAYING)
        bus = self.pipeline.get_bus()
        while True:
            msg = bus.timed_pop_filtered(
                Gst.SECOND,
                Gst.MessageType.ERROR | Gst.MessageType.EOS | Gst.MessageType.WARNING
            )

            if msg:
                if msg.type == Gst.MessageType.ERROR:
                    err, debug = msg.parse_error()
                    print(f"Error de GStreamer: {err}, {debug}")
                    break
                elif msg.type == Gst.MessageType.WARNING:
                    warn, debug = msg.parse_warning()
                    print(f"Advertencia de GStreamer: {warn}, {debug}")
                elif msg.type == Gst.MessageType.EOS:
                    print("Fin del stream.")
                    break

    @Slot()
    def on_new_sample(self, sink):
        sample = sink.emit("pull-sample")
        if not sample:
            return Gst.FlowReturn.ERROR

        buffer = sample.get_buffer()
        caps = sample.get_caps()
        width = caps.get_structure(0).get_value('width')
        height = caps.get_structure(0).get_value('height')

        success, map_info = buffer.map(Gst.MapFlags.READ)
        if not success:
            return Gst.FlowReturn.ERROR

        try:
            frame = np.frombuffer(map_info.data, np.uint8).reshape((height, width, 3))
            image = QImage(frame.data, width, height, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image)

            # Mostrar en la cámara 1
            self.labels[0].setPixmap(pixmap.scaled(self.labels[0].size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        finally:
            buffer.unmap(map_info)

        return Gst.FlowReturn.OK

    def closeEvent(self, event):
        self.pipeline.set_state(Gst.State.NULL)
        event.accept()