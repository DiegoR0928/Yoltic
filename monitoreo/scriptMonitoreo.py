import asyncio
import websockets
import psutil
import json

async def enviar_datos():
    """
    Establece una conexión WebSocket con un servidor remoto y envía periódicamente 
    datos del uso de CPU y disco del sistema.

    La función intenta conectarse al WebSocket en la URI especificada y, una vez 
    conectado, envía un mensaje JSON con el porcentaje de uso de CPU y disco cada segundo.

    En caso de una desconexión o error, espera 5 segundos y vuelve a intentar la conexión 
    de manera indefinida.

    Notas:
    - La URI del WebSocket debe ser reemplazada según la configuración del servidor.
    - Usa psutil para obtener métricas del sistema.
    - Usa asyncio para la ejecución asíncrona y manejo de la conexión.
    """
    uri = "ws://192.168.1.75:8000/ws/monitoreo/"  # Reemplaza con tu IP/Dominio
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                while True:
                    cpu = psutil.cpu_percent(interval=1)
                    disco = psutil.disk_usage('/').percent

                    mensaje = json.dumps({
                        "cpu": cpu,
                        "disco": disco
                    })

                    await websocket.send(mensaje)
                    await asyncio.sleep(1)  # Espera 3 segundos entre envíos
        except Exception as e:
            print(f"Error de conexión: {e}. Reintentando en 5 segundos...")
            await asyncio.sleep(5)

asyncio.run(enviar_datos())
