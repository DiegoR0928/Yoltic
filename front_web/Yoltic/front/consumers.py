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

        reader, writer = await asyncio.open_connection('127.0.0.1', 5000)
        logging.info("Conectado a GStreamer en 127.0.0.1:5000")

        try:
            buffer = b''
            while True:
                data = await reader.read(4096)
                if not data:
                    logging.error("No hay datos del stream, terminando conexión.")
                    break

                buffer += data
                
                # Buscar marcadores de inicio/fin de JPEG (0xFFD8 y 0xFFD9)
                start_marker = b'\xff\xd8'
                end_marker = b'\xff\xd9'
                
                while True:
                    start_pos = buffer.find(start_marker)
                    if start_pos == -1:
                        buffer = b''
                        break
                    
                    end_pos = buffer.find(end_marker, start_pos)
                    if end_pos == -1:
                        break
                    
                    # Extraer frame JPEG completo
                    jpeg_frame = buffer[start_pos:end_pos+2]
                    buffer = buffer[end_pos+2:]
                    
                    # Construir y enviar parte del MJPEG
                    boundary = b'--frame\r\n'
                    content_type = b'Content-Type: image/jpeg\r\n\r\n'
                    frame_data = boundary + content_type + jpeg_frame + b'\r\n'
                    
                    try:
                        await self.send_body(frame_data, more_body=True)
                        logging.debug(f"[STREAM] Enviado frame de {len(jpeg_frame)} bytes")
                    except Exception as send_error:
                        logging.error(f"Error al enviar frame: {send_error}")
                        raise
                    
                await asyncio.sleep(0.01)
                
        except Exception as e:
            logging.error(f"Error en MJPEG stream: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
            logging.info("Conexión cerrada.")