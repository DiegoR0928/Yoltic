# app/consumers.py
import json
import socket
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.generic.http import AsyncHttpConsumer
import asyncio
import logging
import time


class JoystickConsumer(AsyncWebsocketConsumer):
    """
    Consumer WebSocket para recibir comandos del joystick desde el frontend
    y enviar dichos comandos mediante UDP a un dispositivo (robot).
    """

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            x = data.get('x')
            y = data.get('y')
            if x is not None and y is not None:
                UDP_IP = "192.168.1.83"
                UDP_PORT = 5005
                mensaje = f"{x},{y}"
                await asyncio.get_running_loop().run_in_executor(
                    None,
                    self.enviar_udp,
                    mensaje,
                    UDP_IP,
                    UDP_PORT
                )
                print(f"Enviado: {mensaje} a {UDP_IP}:{UDP_PORT}")
        except Exception as e:
            print("Error:", e)

    def enviar_udp(self, mensaje, ip, puerto):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(mensaje.encode('utf-8'), (ip, puerto))
        sock.close()


class BaseMjpegStreamConsumer(AsyncHttpConsumer):
    udp_port = None

    async def handle(self, body):
        self.response_headers = [
            (b"Content-Type", b"multipart/x-mixed-replace; boundary=frame"),
            (b"Cache-Control", b"no-cache, no-store, must-revalidate"),
            (b"Pragma", b"no-cache"),
            (b"Expires", b"0"),
        ]
        await self.send_headers(headers=self.response_headers)

        self._active_tasks = set()
        self.protocol = MJPEGProtocol(self.send_frame_safe, self._active_tasks)
        self.transport = None

        try:
            loop = asyncio.get_running_loop()
            self.transport, _ = await loop.create_datagram_endpoint(
                lambda: self.protocol,
                local_addr=('0.0.0.0', self.udp_port)
            )
            logging.info(
                f"Esperando video MJPEG por UDP en 0.0.0.0:{self.udp_port}"
            )

            while not self.protocol.done:
                await asyncio.sleep(1)

        except asyncio.CancelledError:
            logging.info("Stream cancelado por el cliente.")
        except Exception as e:
            logging.error(f"Error en MJPEG stream: {e}")
        finally:
            await self.cleanup()

    async def send_frame_safe(self, frame_data):
        try:
            await self.send_body(frame_data, more_body=True)
        except Exception as e:
            logging.error(f"Error enviando frame: {e}")
            self.protocol.done = True

    async def cleanup(self):
        if self.transport:
            self.transport.close()
        self.protocol.done = True
        for task in self._active_tasks:
            task.cancel()
        if self._active_tasks:
            await asyncio.gather(*self._active_tasks, return_exceptions=True)
        logging.info("MJPEG stream limpiado completamente.")


class MJPEGProtocol(asyncio.DatagramProtocol):
    def __init__(self, send_frame_callback, active_tasks):
        super().__init__()
        self.send_frame = send_frame_callback
        self.active_tasks = active_tasks
        self.buffer = bytearray()
        self.last_frame_time = None
        self.transport = None
        self.done = False

    def connection_made(self, transport):
        self.transport = transport
        print(
            "✅ Conexión UDP establecida en",
            transport.get_extra_info('sockname')
        )

    def datagram_received(self, data, addr):
        try:
            self.last_frame_time = time.time()
            self.buffer.extend(data)

            while True:
                start_pos = self.buffer.find(b'\xff\xd8')
                if start_pos == -1:
                    self.buffer.clear()
                    break

                end_pos = self.buffer.find(b'\xff\xd9', start_pos + 2)
                if end_pos == -1:
                    break

                jpeg_frame = bytes(self.buffer[start_pos:end_pos + 2])
                self.buffer = self.buffer[end_pos + 2:]

                frame_data = (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' +
                    jpeg_frame +
                    b'\r\n'
                )

                task = asyncio.create_task(self.send_frame(frame_data))
                task.add_done_callback(lambda t: self.active_tasks.discard(t))
                self.active_tasks.add(task)

        except Exception as e:
            print(f"❌ Error procesando datagrama: {str(e)}")
            self.done = True

    def error_received(self, exc):
        print(f"❌ Error en conexión UDP: {str(exc)}")
        self.done = True

    def connection_lost(self, exc):
        if exc:
            print(f"⚠️ Conexión UDP perdida: {str(exc)}")
        else:
            print("🔌 Conexión UDP cerrada normalmente")
        self.done = True


class MjpegStreamConsumer(BaseMjpegStreamConsumer):
    udp_port = 5000


class MjpegStreamConsumer2(BaseMjpegStreamConsumer):
    udp_port = 5001


class MjpegStreamConsumer3(BaseMjpegStreamConsumer):
    udp_port = 5002


class MonitoreoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("monitoreo", self.channel_name)
        await self.accept()
        print("Cliente conectado al monitoreo")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("monitoreo", self.channel_name)
        print("Cliente desconectado")

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            "monitoreo",
            {
                "type": "enviar_datos",
                "cpu": data.get("cpu"),
                "disco": data.get("disco")
            }
        )

    async def enviar_datos(self, event):
        await self.send(text_data=json.dumps({
            "cpu": event["cpu"],
            "disco": event["disco"]
        }))

