import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
import os
import time
from datetime import datetime
import threading

Gst.init(None)

class GrabacionPipeline:
    def __init__(self, rtsp_url, output_dir, camera_id):
        self.rtsp_url = rtsp_url
        self.output_dir = output_dir
        self.camera_id = camera_id
        self.pipeline = None
        self.is_recording = False
        self.lock = threading.Lock()
        self._ensure_output_dir()

    def _ensure_output_dir(self):
        os.makedirs(self.output_dir, exist_ok=True)

    def _build_pipeline(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_file = os.path.join(self.output_dir, f"grabacion_{self.camera_id}_{timestamp}.mp4")
        
        print(f"[Cámara {self.camera_id}] 🎥 Configurando grabación en {self.output_file}")

        # Crear pipeline
        self.pipeline = Gst.Pipeline.new(f"recording-{self.camera_id}")
        
        # Elementos
        self.src = Gst.ElementFactory.make("rtspsrc", f"src-{self.camera_id}")
        self.src.set_property("location", self.rtsp_url)
        self.src.set_property("latency", 200)
        self.src.set_property("drop-on-latency", True)
        
        self.depay = Gst.ElementFactory.make("rtph264depay", f"depay-{self.camera_id}")
        self.parse = Gst.ElementFactory.make("h264parse", f"parse-{self.camera_id}")
        self.mux = Gst.ElementFactory.make("mp4mux", f"mux-{self.camera_id}")
        self.mux.set_property("faststart", True)
        
        self.sink = Gst.ElementFactory.make("filesink", f"sink-{self.camera_id}")
        self.sink.set_property("location", self.output_file)
        self.sink.set_property("sync", False)
        self.sink.set_property("async", False)

        # Agregar elementos
        for elem in [self.src, self.depay, self.parse, self.mux, self.sink]:
            if not elem:
                print(f"[Cámara {self.camera_id}] ❌ Error al crear elemento")
                return False
            self.pipeline.add(elem)

        # Conexión de elementos
        def on_pad_added(src, new_pad):
            sink_pad = self.depay.get_static_pad("sink")
            if sink_pad.is_linked():
                return
            
            new_pad.link(sink_pad)

        self.src.connect("pad-added", on_pad_added)
        self.depay.link(self.parse)
        self.parse.link(self.mux)
        self.mux.link(self.sink)

        # Configurar bus
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self._on_message)
        
        return True

    def _on_message(self, bus, message):
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

    def start(self):
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
                print(f"[Cámara {self.camera_id}] ❌ Error al iniciar grabación")
                return False

    def stop(self):
        with self.lock:
            if not self.is_recording:
                return True

            print(f"[Cámara {self.camera_id}] ⏹️ Finalizando grabación...")
            
            # Enviar EOS
            self.pipeline.send_event(Gst.Event.new_eos())
            
            # Esperar EOS con timeout
            start_time = time.time()
            while self.is_recording and (time.time() - start_time) < 5:  # 5 seg timeout
                time.sleep(0.1)

            # Forzar detención si es necesario
            if self.is_recording:
                self.pipeline.set_state(Gst.State.NULL)
                self.is_recording = False
                print(f"[Cámara {self.camera_id}] ⚠️ Grabación detenida por timeout")

            # Verificar archivo
            if os.path.exists(self.output_file):
                size = os.path.getsize(self.output_file)
                print(f"[Cámara {self.camera_id}] 💾 Archivo guardado ({size} bytes)")
                return True
            else:
                print(f"[Cámara {self.camera_id}] ❌ Archivo no se creó correctamente")
                return False
