import gi
import os
import time
import threading

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject, GLib
from django.conf import settings

Gst.init(None)

class CameraPipeline:
    def __init__(self, rtsp_url, udp_port, record_path):
        self.rtsp_url = rtsp_url
        self.udp_port = udp_port
        self.record_path = record_path
        self.pipeline = None
        self.tee = None
        self.recording_bin = None
        self.recording_pad = None
        self.recording_enabled = False
        self.lock = threading.Lock()  # Para sincronización de threads
        self.main_loop = GLib.MainLoop()

        self._build_pipeline()

    def _build_pipeline(self):
        print(f"🚀 Inicializando pipeline para {self.rtsp_url} en puerto {self.udp_port}")

        self.pipeline = Gst.Pipeline.new(f"pipeline-{self.udp_port}")

        # Configurar bus para manejar mensajes
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self._on_message)

        # Elemento rtspsrc
        self.src = Gst.ElementFactory.make("rtspsrc", "src")
        self.src.set_property("location", self.rtsp_url)
        self.src.set_property("latency", 120)
        self.src.set_property("drop-on-latency", True)
        self.src.connect("pad-added", self._on_pad_added)

        self.pipeline.add(self.src)

    def _on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print(f"❌ Error: {err.message}")
            self.main_loop.quit()
        elif t == Gst.MessageType.EOS:
            print("🔚 Fin del stream")
            self.main_loop.quit()
        elif t == Gst.MessageType.STATE_CHANGED:
            if isinstance(message.src, Gst.Pipeline):
                old, new, pending = message.parse_state_changed()
                print(f"🔄 Cambio de estado: {old.value_nick} -> {new.value_nick}")

    def _on_pad_added(self, src, pad):
        print(f"🎯 Pad agregado desde rtspsrc: {pad.get_name()}")

        # Crear decodebin dinámicamente
        decodebin = Gst.ElementFactory.make("decodebin", "decodebin")
        decodebin.connect("pad-added", self._on_decodebin_pad_added)
        decodebin.connect("no-more-pads", lambda x: print("ℹ️ No hay más pads en decodebin"))

        self.pipeline.add(decodebin)
        decodebin.sync_state_with_parent()

        # Conectar el pad del src al decodebin
        sink_pad = decodebin.get_static_pad("sink")
        if not sink_pad.is_linked():
            pad.link(sink_pad)

    def _on_decodebin_pad_added(self, decodebin, pad):
        caps = pad.get_current_caps()
        if not caps:
            print("⚠️ Pad sin caps, ignorando")
            return

        structure = caps.get_structure(0)
        media_type = structure.get_name()
        print(f"🧩 Pad agregado desde decodebin: {pad.get_name()} ({media_type})")

        if not media_type.startswith("video/x-raw"):
            print("🔇 Ignorando pad que no es video")
            return

        with self.lock:
            if hasattr(self, 'tee') and self.tee:
                print("⏭️ Ya existe un tee conectado")
                return

            print("📡 Configurando elementos de video...")

            # Elementos comunes de procesamiento de video
            videoconvert = Gst.ElementFactory.make("videoconvert", "videoconvert")
            videorate = Gst.ElementFactory.make("videorate", "videorate")
            videoscale = Gst.ElementFactory.make("videoscale", "videoscale")
            capsfilter = Gst.ElementFactory.make("capsfilter", "capsfilter")
            capsfilter.set_property("caps", Gst.Caps.from_string("video/x-raw,framerate=10/1,width=240,height=120"))

            # Configurar tee
            self.tee = Gst.ElementFactory.make("tee", "tee")
            self.tee.set_property("allow-not-linked", True)

            # Configurar rama de transmisión UDP
            jpegenc = Gst.ElementFactory.make("jpegenc", "jpegenc")
            udpsink = Gst.ElementFactory.make("udpsink", "udpsink")
            udpsink.set_property("host", "127.0.0.1")
            udpsink.set_property("port", self.udp_port)
            udpsink.set_property("sync", False)
            udpsink.set_property("async", False)

            # Agregar todos los elementos al pipeline
            for elem in [videoconvert, videorate, videoscale, capsfilter, 
                        self.tee, jpegenc, udpsink]:
                self.pipeline.add(elem)
                elem.sync_state_with_parent()

            # Conectar los elementos
            pad.link(videoconvert.get_static_pad("sink"))
            videoconvert.link(videorate)
            videorate.link(videoscale)
            videoscale.link(capsfilter)
            capsfilter.link(self.tee)

            # Rama de transmisión UDP
            queue_udp = Gst.ElementFactory.make("queue", "queue_udp")
            self.pipeline.add(queue_udp)
            queue_udp.sync_state_with_parent()

            self.tee.link(queue_udp)
            queue_udp.link(jpegenc)
            jpegenc.link(udpsink)

            print("✅ Pipeline armado correctamente")

    def enable_record(self):
        with self.lock:
            if self.recording_enabled:
                print("⚠️ Grabación ya habilitada")
                return

            if not self.tee:
                print("❌ Tee no disponible, no se puede habilitar grabación")
                return

            print("🎥 Habilitando grabación...")

            try:
                # Crear elementos de grabación
                queue_rec = Gst.ElementFactory.make("queue", "queue_rec")
                capsfilter_enc = Gst.ElementFactory.make("capsfilter", "capsfilter_enc")
                capsfilter_enc.set_property("caps", Gst.Caps.from_string("video/x-raw,format=I420"))
                
                enc = Gst.ElementFactory.make("x264enc", "x264enc")
                enc.set_property("tune", "zerolatency")
                enc.set_property("speed-preset", "ultrafast")
                enc.set_property("key-int-max", 30)
                enc.set_property("bitrate", 2048)
                
                mux = Gst.ElementFactory.make("qtmux", "qtmux")
                mux.set_property("faststart", True)  # Para moov al inicio
                mux.set_property("fragment-duration", 1000)
                sink = Gst.ElementFactory.make("filesink", "filesink")
                
                filename = os.path.join(self.record_path, f"grabacion_{int(time.time())}.mp4")
                sink.set_property("location", filename)

                # Agregar elementos al pipeline
                for elem in [queue_rec, capsfilter_enc, enc, mux, sink]:
                    self.pipeline.add(elem)
                    elem.sync_state_with_parent()

                # Conectar elementos
                queue_rec.link(capsfilter_enc)
                capsfilter_enc.link(enc)
                enc.link(mux)
                mux.link(sink)

                # Conectar al tee
                tee_src_pad = self.tee.get_request_pad("src_%u")
                queue_sink_pad = queue_rec.get_static_pad("sink")
                
                if tee_src_pad and queue_sink_pad:
                    tee_src_pad.link(queue_sink_pad)
                    self.recording_pad = tee_src_pad
                    self.recording_enabled = True
                    print(f"💾 Grabando en archivo: {filename}")
                else:
                    print("❌ No se pudo conectar la rama de grabación")
                    # Limpiar elementos si falla
                    for elem in [queue_rec, capsfilter_enc, enc, mux, sink]:
                        elem.set_state(Gst.State.NULL)
                        self.pipeline.remove(elem)

            except Exception as e:
                print(f"❌ Error al habilitar grabación: {str(e)}")

    def disable_record(self):
        with self.lock:
            if not self.recording_enabled:
                print("⚠️ Grabación no está activa")
                return False

            print("🛑 Iniciando cierre controlado de grabación...")
            
            try:
                # 1. Obtener el muxer y filesink
                mux = self.pipeline.get_by_name("qtmux")
                filesink = self.pipeline.get_by_name("filesink")
                
                if not mux or not filesink:
                    print("❌ Elementos de grabación no encontrados")
                    return False

                # 2. Enviar EOS directamente al muxer
                print("📤 Enviando EOS al pipeline...")
                if not mux.send_event(Gst.Event.new_eos()):
                    print("⚠️ No se pudo enviar EOS, forzando cierre")

                # 3. Esperar EOS con timeout
                start_time = time.time()
                eos_received = False
                
                while time.time() - start_time < 5:  # 5 segundos máximo
                    msg = self.bus.pop_filtered(
                        Gst.MessageType.EOS | Gst.MessageType.ERROR
                    )
                    
                    if msg and msg.type == Gst.MessageType.EOS:
                        print("✅ EOS recibido, archivo completo")
                        eos_received = True
                        break
                    
                    time.sleep(0.1)

                # 4. Cerrar archivo manualmente si es necesario
                if not eos_received:
                    print("⚠️ Timeout EOS, cerrando archivo manualmente")
                    filesink.set_property("async", False)
                    filesink.set_state(Gst.State.NULL)

                # 5. Limpieza de elementos
                self._clean_recording_elements()
                
                # 6. Reinicio completo del pipeline
                print("🔄 Reiniciando pipeline...")
                self._restart_pipeline()
                
                return True

            except Exception as e:
                print(f"🔥 Error crítico: {str(e)}")
                return False

    def _clean_recording_elements(self):
        """Limpia solo los elementos de grabación"""
        elements = [
            self.pipeline.get_by_name("queue_rec"),
            self.pipeline.get_by_name("capsfilter_enc"),
            self.pipeline.get_by_name("x264enc"),
            self.pipeline.get_by_name("qtmux"),
            self.pipeline.get_by_name("filesink")
        ]
        
        for elem in elements:
            if elem:
                elem.set_state(Gst.State.NULL)
                self.pipeline.remove(elem)
        
        if self.recording_pad:
            self.tee.release_request_pad(self.recording_pad)
            self.recording_pad = None
        
        self.recording_enabled = False

    def _restart_pipeline(self):
        """Reinicia completamente el pipeline manteniendo la conexión RTSP"""
        print("🔧 Reinicio completo del pipeline...")
        
        # 1. Guardar estado actual
        was_playing = self.pipeline.current_state == Gst.State.PLAYING
        rtsp_url = self.src.get_property("location")
        
        # 2. Detener y limpiar pipeline
        self.pipeline.set_state(Gst.State.NULL)
        
        # 3. Reconstruir pipeline desde cero
        self._build_pipeline()
        
        # 4. Restaurar conexión RTSP
        self.src.set_property("location", rtsp_url)
        
        # 5. Volver a estado anterior
        if was_playing:
            self.pipeline.set_state(Gst.State.PLAYING)
            print("▶️ Pipeline reiniciado y en reproducción")
        else:
            print("⏸️ Pipeline reiniciado (en pausa)")

    def start(self):
        print("▶️ Iniciando pipeline...")
        self.pipeline.set_state(Gst.State.PLAYING)
        
        # Iniciar el main loop en un hilo separado
        def run_main_loop():
            self.main_loop.run()

        threading.Thread(target=run_main_loop, daemon=True).start()
        print("✅ Pipeline iniciado")

    def stop(self):
        print("⏹️ Deteniendo pipeline...")
        self.main_loop.quit()
        self.pipeline.set_state(Gst.State.NULL)
        print("✅ Pipeline detenido")

    # Añade estos métodos a tu clase CameraPipeline
    def restart_udp_stream(self):
        """Reinicia el stream UDP para esta cámara"""
        print(f"🔄 Reiniciando stream UDP para cámara {self.udp_port}")
        
        # 1. Detener el pipeline temporalmente
        was_playing = self.pipeline.current_state == Gst.State.PLAYING
        if was_playing:
            self.pipeline.set_state(Gst.State.PAUSED)
        
        # 2. Buscar y remover elementos UDP específicos
        udpsink = self.pipeline.get_by_name("udpsink")
        queue_udp = self.pipeline.get_by_name("queue_udp")
        jpegenc = self.pipeline.get_by_name("jpegenc")
        
        if udpsink:
            # Desconectar elementos
            self.tee.unlink(queue_udp)
            queue_udp.unlink(jpegenc)
            jpegenc.unlink(udpsink)
            
            # Remover elementos
            for elem in [udpsink, queue_udp, jpegenc]:
                elem.set_state(Gst.State.NULL)
                self.pipeline.remove(elem)
        
        # 3. Recrear la rama UDP
        print("🔧 Reconstruyendo rama UDP...")
        queue_udp = Gst.ElementFactory.make("queue", "queue_udp")
        jpegenc = Gst.ElementFactory.make("jpegenc", "jpegenc")
        udpsink = Gst.ElementFactory.make("udpsink", "udpsink")
        
        udpsink.set_property("host", "127.0.0.1")
        udpsink.set_property("port", self.udp_port)
        udpsink.set_property("sync", False)
        udpsink.set_property("async", False)
        
        # Agregar al pipeline
        for elem in [queue_udp, jpegenc, udpsink]:
            self.pipeline.add(elem)
        
        # Reconectar
        self.tee.link(queue_udp)
        queue_udp.link(jpegenc)
        jpegenc.link(udpsink)
        
        # Sincronizar estados
        for elem in [queue_udp, jpegenc, udpsink]:
            elem.sync_state_with_parent()
        
        # 4. Reanudar si estaba en play
        if was_playing:
            self.pipeline.set_state(Gst.State.PLAYING)
        
        print(f"✅ Stream UDP reiniciado en puerto {self.udp_port}")

class MultiCameraController:
    def __init__(self):
        self.cameras = []
        self.lock = threading.Lock()

    def add_camera(self, rtsp_url, udp_port, record_path):
        with self.lock:
            camera = CameraPipeline(rtsp_url, udp_port, record_path)
            self.cameras.append(camera)
            camera.start()

    def enable_record(self):
        with self.lock:
            for cam in self.cameras:
                cam.enable_record()

    def disable_record(self):
        with self.lock:
            for cam in self.cameras:
                cam.disable_record()

    def stop_all(self):
        with self.lock:
            for cam in self.cameras:
                cam.stop()
            self.cameras.clear()


_controller = None

def get_controlador_pipeline():
    global _controller
    if _controller is None:
        print("🆕 Inicializando pipelines de cámara...")
        _controller = MultiCameraController()
        _controller.add_camera("rtsp://192.168.1.74:8554/cam1", 5000, settings.MEDIA_ROOT)
        _controller.add_camera("rtsp://192.168.1.74:8554/cam2", 5001, settings.MEDIA_ROOT)
        _controller.add_camera("rtsp://192.168.1.74:8554/cam3", 5002, settings.MEDIA_ROOT)
    return _controller
