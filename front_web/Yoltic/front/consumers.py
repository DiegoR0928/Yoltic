# app/consumers.py
import json
import socket
from channels.generic.websocket import WebsocketConsumer
from channels.generic.http import AsyncHttpConsumer
import asyncio
import logging

class JoystickConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        try:
            data = json.loads(text_data)
            x = data.get('x')
            y = data.get('y')
            if x is not None and y is not None:
                UDP_IP = "192.168.1.106"
                UDP_PORT = 5005
                mensaje = f"{x},{y}"
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(mensaje.encode('utf-8'), (UDP_IP, UDP_PORT))
                print(f"Enviado: {mensaje} a {UDP_IP}:{UDP_PORT}")
        except Exception as e:
            print("Error:", e)

class MjpegStreamConsumer(AsyncHttpConsumer):
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
                local_addr=('0.0.0.0', 5000)  # AJUSTA el puerto según sea necesario
            )
            logging.info("Esperando video MJPEG por UDP en 0.0.0.0:5000")

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
            await asyncio.wait(self._active_tasks)
        logging.info("MJPEG stream limpiado completamente.")


class MJPEGProtocol:
    def __init__(self, send_frame, active_tasks):
        self.send_frame = send_frame
        self._active_tasks = active_tasks
        self.buffer = b""
        self.done = False
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        print(f"UDP packet recibido: {len(data)} bytes")
        try:
            self.buffer += data

            # Protege contra buffers demasiado grandes
            if len(self.buffer) > 10_000_000:
                logging.warning("Buffer demasiado grande, limpiando.")
                self.buffer = b""

            start_marker = b'\xff\xd8'
            end_marker = b'\xff\xd9'

            while True:
                start_pos = self.buffer.find(start_marker)
                if start_pos == -1:
                    self.buffer = b''
                    break

                end_pos = self.buffer.find(end_marker, start_pos)
                if end_pos == -1:
                    break

                jpeg_frame = self.buffer[start_pos:end_pos + 2]
                self.buffer = self.buffer[end_pos + 2:]

                boundary = b'--frame\r\n'
                content_type = b'Content-Type: image/jpeg\r\n\r\n'
                frame_data = boundary + content_type + jpeg_frame + b'\r\n'

                task = asyncio.create_task(self.send_frame(frame_data))
                task.add_done_callback(self._remove_task)
                self._active_tasks.add(task)

        except Exception as e:
            logging.error(f"Error procesando datagrama UDP: {e}")
            self.done = True

    def _remove_task(self, task):
        self._active_tasks.discard(task)

    def connection_lost(self, exc):
        self.done = True
        if exc:
            logging.error(f"Conexión UDP perdida: {exc}")
        else:
            logging.info("Conexión UDP cerrada normalmente.")
