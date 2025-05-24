"""
Módulo para gestionar la grabación de streams RTSP a archivos MP4 usando
GStreamer.
"""

from typing import Optional
import threading
from datetime import datetime
import time
import os
from gi.repository import Gst
import gi
gi.require_version('Gst', '1.0')

Gst.init(None)


class GrabacionPipeline:
    """
    Clase que encapsula un pipeline de GStreamer para grabar una transmisión
    RTSP a un archivo MP4.

    Atributos:
        rtsp_url (str): URL del stream RTSP.
        output_dir (str): Directorio donde se guardarán los archivos grabados.
        camera_id (str): Identificador único de la cámara.
    """

    def __init__(self, rtsp_url: str, output_dir: str, camera_id: str) -> None:
        """
        Inicializa la instancia con la URL RTSP, directorio de salida y ID
        de cámara.

        Args:
            rtsp_url (str): URL del stream RTSP.
            output_dir (str): Directorio para guardar archivos.
            camera_id (str): Identificador único de la cámara.
        """
        self.rtsp_url: str = rtsp_url
        self.output_dir: str = output_dir
        self.camera_id: str = camera_id
        self.pipeline: Optional[Gst.Pipeline] = None
        self.is_recording: bool = False
        self.lock: threading.Lock = threading.Lock()
        self.output_file: Optional[str] = None
        self._ensure_output_dir()

    def _ensure_output_dir(self) -> None:
        """
        Crea el directorio de salida si no existe.

        No recibe ni devuelve nada.
        """
        os.makedirs(self.output_dir, exist_ok=True)

    def _build_pipeline(self) -> bool:
        """
        Construye y configura el pipeline GStreamer para la grabación.

        Crea todos los elementos necesarios, los
        agrega al pipeline y los conecta
        entre sí. También configura el bus para manejar mensajes del pipeline.

        Returns:
            bool: True si el pipeline se construyó correctamente, False en caso
                  contrario.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_file = os.path.join(
            self.output_dir,
            f"grabacion_{self.camera_id}_{timestamp}.mp4"
        )
        print(
            f"[Cámara {self.camera_id}] 🎥 Configurando grabación en "
            f"{self.output_file}"
        )

        self.pipeline = Gst.Pipeline.new(f"recording-{self.camera_id}")

        self.src = Gst.ElementFactory.make(
            "rtspsrc", f"src-{self.camera_id}"
        )
        self.src.set_property("location", self.rtsp_url)
        self.src.set_property("latency", 200)
        self.src.set_property("drop-on-latency", True)

        self.depay = Gst.ElementFactory.make(
            "rtph264depay", f"depay-{self.camera_id}"
        )
        self.parse = Gst.ElementFactory.make(
            "h264parse", f"parse-{self.camera_id}"
        )
        self.mux = Gst.ElementFactory.make(
            "mp4mux", f"mux-{self.camera_id}"
        )
        self.mux.set_property("faststart", True)

        self.sink = Gst.ElementFactory.make(
            "filesink", f"sink-{self.camera_id}"
        )
        self.sink.set_property(
            "location",
            self.output_file
        )
        self.sink.set_property("sync", False)
        self.sink.set_property("async", False)

        for elem in [self.src, self.depay, self.parse, self.mux, self.sink]:
            if not elem:
                print(f"[Cámara {self.camera_id}] ❌ Error al crear elemento")
                return False
            self.pipeline.add(elem)

        def on_pad_added(src, new_pad) -> None:
            """
            Callback que se ejecuta cuando 'rtspsrc'
            agrega un nuevo pad dinámicamente.

            Intenta enlazar el nuevo pad con el sink
            pad del depayloader si no está
            enlazado aún.

            Args:
                src: Elemento que genera el pad (rtspsrc).
                new_pad: El nuevo pad que se agrega dinámicamente.
            """
            sink_pad = self.depay.get_static_pad("sink")
            if sink_pad.is_linked():
                return
            new_pad.link(sink_pad)

        self.src.connect("pad-added", on_pad_added)
        self.depay.link(self.parse)
        self.parse.link(self.mux)
        self.mux.link(self.sink)

        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self._on_message)

        return True

    def _on_message(self, bus: Gst.Bus, message: Gst.Message) -> None:
        """
        Manejador de mensajes del bus del pipeline.

        Detecta eventos de fin de stream (EOS) o errores
        y actúa en consecuencia.

        Args:
            bus (Gst.Bus): El bus de mensajes del pipeline.
            message (Gst.Message): El mensaje recibido.
        """
        if message.type == Gst.MessageType.EOS:
            print(f"[Cámara {self.camera_id}] ✅ Grabación completada")
            with self.lock:
                self.is_recording = False
        elif message.type == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print(f"[Cámara {self.camera_id}] ❌ Error: {err.message}")
            if debug:
                print(f"[Cámara {self.camera_id}] Debug: {debug}")
            self.stop()

    def start(self) -> bool:
        """
        Inicia la grabación si no está grabando.

        Construye el pipeline y pone el estado en PLAYING.

        Returns:
            bool: True si la grabación se inició
            correctamente, False si ya estaba
                  grabando o falló.
        """
        with self.lock:
            if self.is_recording:
                print(f"[Cámara {self.camera_id}] ⚠️ Ya está grabando")
                return False

            if not self._build_pipeline():
                return False

            ret = self.pipeline.set_state(Gst.State.PLAYING)
            if ret == Gst.StateChangeReturn.SUCCESS:
                print(f"[Cámara {self.camera_id}] ⏺️ Grabación iniciada")
                self.is_recording = True
                return True
            else:
                print(
                    f"[Cámara {self.camera_id}] ❌ Error al iniciar grabación"
                )
                return False

    def stop(self) -> bool:
        """
        Detiene la grabación enviando un evento EOS al pipeline.

        Espera que el pipeline termine o fuerza la detención tras timeout.

        Returns:
            bool: True si la grabación se detuvo y
            el archivo se guardó, False si
                hubo error.
        """
        with self.lock:
            if not self.is_recording:
                return True

            print(f"[Cámara {self.camera_id}] ⏹️ Finalizando grabación...")
            self.pipeline.send_event(Gst.Event.new_eos())

            start_time = time.time()
            while self.is_recording and (time.time() - start_time) < 5:
                time.sleep(0.1)

            if self.is_recording:
                self.pipeline.set_state(Gst.State.NULL)
                self.is_recording = False
                print(
                    f"[Cámara {self.camera_id}] ⚠️ Grabación detenida "
                    "por timeout"
                )

            if self.output_file and os.path.exists(self.output_file):
                size = os.path.getsize(self.output_file)
                print(
                    f"[Cámara {self.camera_id}] 💾 Archivo guardado "
                    f"({size} bytes)"
                )
                return True
            else:
                print(
                    f"[Cámara {self.camera_id}] ❌ Archivo no se creó "
                    "correctamente"
                )
                return False

