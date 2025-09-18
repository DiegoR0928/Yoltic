import time
from gi.repository import Gst
import gi
gi.require_version('Gst', '1.0')

class LivePipeline:
    """
    Clase para manejar un pipeline de GStreamer que recibe un stream RTSP,
    lo decodifica, convierte a JPEG y lo envía por UDP a un puerto local.
    """

    def __init__(self, rtsp_url, udp_port):
        """
        Inicializa la clase con la URL RTSP y el puerto UDP de destino.

        Args:
            rtsp_url (str): URL del stream RTSP a recibir.
            udp_port (int): Puerto UDP donde se enviará el stream JPEG.
        """
        self.rtsp_url = rtsp_url
        self.udp_port = udp_port
        self.pipeline = None
        self.src = None
        self.sink = None
        self._initialize()

    def _initialize(self):
        """
        Inicializa GStreamer y construye el pipeline, además configura el bus.
        """
        Gst.init(None)
        self._build_pipeline()
        self._setup_bus()

    def _build_pipeline(self):
        """
        Construye el pipeline de GStreamer con los elementos necesarios y
        conecta los pads, incluyendo manejo de pads dinámicos de rtspsrc.

        Returns:
            bool: True si se construyó correctamente,
            False si hubo algún error.
        """
        print(
            f"🔴 Configurando pipeline LIVE para "
            f"{self.rtsp_url} en puerto {self.udp_port}"
        )

        # Crear pipeline
        self.pipeline = Gst.Pipeline.new("live-pipeline")

        # Elementos de fuente
        self.src = Gst.ElementFactory.make("rtspsrc", "src")
        self.src.set_property("location", self.rtsp_url)
        self.src.set_property("latency", 800)
        self.src.set_property("drop-on-latency", False)
        self.src.set_property("do-retransmission", True)
        self.src.set_property("udp-reconnect", 5)

        # Elementos de depayload
        self.depay = Gst.ElementFactory.make("rtph264depay", "depay")
        self.parse = Gst.ElementFactory.make("h264parse", "parse")

        # Elementos de decodificación
        self.decode = Gst.ElementFactory.make("avdec_h264", "decode")

        # Elementos de conversión
        self.convert = Gst.ElementFactory.make("videoconvert", "convert")
        self.scale = Gst.ElementFactory.make("videoscale", "scale")
        self.rate = Gst.ElementFactory.make("videorate", "rate")

        # Filtro de capacidades
        self.caps = Gst.ElementFactory.make("capsfilter", "caps")
        self.caps.set_property("caps", Gst.Caps.from_string(
            "video/x-raw,width=640,height=480,framerate=15/1"))

        # Codificación y salida
        self.enc = Gst.ElementFactory.make("jpegenc", "enc")
        self.enc.set_property("quality", 85)
        # Método de compresión mejorado
        self.enc.set_property("idct-method", 2)

        self.sink = Gst.ElementFactory.make("udpsink", "sink")
        self.sink.set_property("host", "127.0.0.1")
        self.sink.set_property("port", self.udp_port)
        self.sink.set_property("sync", False)
        self.sink.set_property("async", True)
        self.sink.set_property("max-lateness", 500000000)  # 500ms
        self.sink.set_property("qos", True)

        # Agregar elementos al pipeline
        elements = [
            self.src, self.depay, self.parse, self.decode,
            self.convert, self.scale, self.rate, self.caps,
            self.enc, self.sink
        ]

        for element in elements:
            if not element:
                print(f"❌ No se pudo crear elemento: {element}")
                return False
            self.pipeline.add(element)

        # Conexión de elementos con manejo de pads dinámicos
        self.src.connect("pad-added", self._on_pad_added)

        # Conectar elementos estáticos
        if not self.depay.link(self.parse):
            print("❌ Error conectando depay a parse")
            return False

        if not self.parse.link(self.decode):
            print("❌ Error conectando parse a decode")
            return False

        if not self.decode.link(self.convert):
            print("❌ Error conectando decode a convert")
            return False

        if not self.convert.link(self.scale):
            print("❌ Error conectando convert a scale")
            return False

        if not self.scale.link(self.rate):
            print("❌ Error conectando scale a rate")
            return False

        if not self.rate.link(self.caps):
            print("❌ Error conectando rate a caps")
            return False

        if not self.caps.link(self.enc):
            print("❌ Error conectando caps a enc")
            return False

        if not self.enc.link(self.sink):
            print("❌ Error conectando enc a sink")
            return False

        return True

    def _on_pad_added(self, src, new_pad):
        """
        Callback para cuando rtspsrc agrega un nuevo pad dinámico.
        Se conecta este pad al depayloader si corresponde.

        Args:
            src (Gst.Element): Elemento que emitió el evento (rtspsrc).
            new_pad (Gst.Pad): Nuevo pad creado.
        """
        print("🎛️ Pad añadido desde rtspsrc")
        sink_pad = self.depay.get_static_pad("sink")

        if sink_pad.is_linked():
            print("⚠️ Pad ya conectado, ignorando")
            return

        caps = new_pad.get_current_caps()
        if not caps:
            print("⚠️ Pad sin caps, ignorando")
            return

        structure = caps.get_structure(0)
        media_type = structure.get_name()

        if media_type.startswith("application/x-rtp"):
            print(f"🔗 Conectando pad RTP (media: {media_type})")
            if new_pad.link(sink_pad) != Gst.PadLinkReturn.OK:
                print("❌ Error conectando pad RTP")
        else:
            print(f"⚠️ Ignorando pad no RTP: {media_type}")

    def _setup_bus(self):
        """
        Configura el bus para escuchar mensajes y eventos del pipeline.
        """
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self._on_message)
        self.bus.enable_sync_message_emission()
        self.bus.connect("sync-message::element", self._on_sync_message)

    def _on_message(self, bus, message):
        """
        Maneja mensajes del bus, incluyendo errores, EOS y cambios de estado.

        Args:
            bus (Gst.Bus): El bus de mensajes del pipeline.
            message (Gst.Message): El mensaje recibido.
        """
        t = message.type
        if t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print(f"❌ Error en pipeline: {err.message}")
            if debug:
                print(f"🔍 Debug info: {debug}")
            self.restart()
        elif t == Gst.MessageType.EOS:
            print("🔚 Fin de transmisión recibido")
        elif t == Gst.MessageType.STATE_CHANGED:
            old, new, pending = message.parse_state_changed()
            print(f"🔄 Cambio de estado: {old.value_nick} -> {new.value_nick}")

    def _on_sync_message(self, bus, message):
        """
        Maneja mensajes sincronizados del bus,
        por ejemplo de elementos específicos.

        Args:
            bus (Gst.Bus): El bus de mensajes del pipeline.
            message (Gst.Message): El mensaje recibido.
        """
        if message.type == Gst.MessageType.ELEMENT:
            if message.get_structure().get_name() == "GstUDPSink":
                print("📤 Mensaje de UDP sink recibido")

    def start(self):
        """
        Inicia la reproducción del pipeline.

        Returns:
            bool: True si el pipeline arrancó correctamente, False si falló.
        """
        print(f"▶️ Iniciando transmisión en puerto {self.udp_port}")
        ret = self.pipeline.set_state(Gst.State.PLAYING)
        if ret == Gst.StateChangeReturn.FAILURE:
            print("❌ Error al iniciar pipeline")
            return False
        return True

    def stop(self):
        """
        Detiene la reproducción del pipeline y lo pone en estado NULL.
        """
        print("⏹️ Deteniendo transmisión")
        self.pipeline.set_state(Gst.State.NULL)

    def restart(self):
        """
        Reinicia el pipeline en caso de error u otro evento que lo requiera.
        """
        print("🔄 Reiniciando pipeline...")
        self.stop()
        time.sleep(1)
        self._initialize()
        self.start()

