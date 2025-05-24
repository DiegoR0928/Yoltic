"""
Script para controlar un Arduino mediante
comandos UDP enviados desde un joystick.

Este programa escucha en un puerto UDP
los comandos de dirección (eje X, eje Y) y
los traduce en comandos de movimiento que se
envían por puerto serial a un Arduino.
"""

import serial
import socket
import time


def inicializar_arduino(puerto: str = '/dev/ttyUSB0', baudios: int = 9600,
                        espera: float = 2.0) -> serial.Serial:
    """
    Inicializa la conexión serial con el Arduino.

    Args:
        puerto (str): Puerto serial donde está conectado el Arduino.
        baudios (int): Tasa de baudios para la comunicación serial.
        espera (float): Tiempo de espera en segundos para
        estabilizar la conexión.

    Returns:
        serial.Serial: Objeto de conexión serial ya abierto.
    """
    arduino = serial.Serial(puerto, baudios, timeout=1)
    time.sleep(espera)
    return arduino


def configurar_socket_udp(ip: str = "0.0.0.0",
                          puerto: int = 5005) -> socket.socket:
    """
    Configura el socket UDP para recibir comandos.

    Args:
        ip (str): Dirección IP en la que escuchar.
        puerto (int): Puerto UDP a usar.

    Returns:
        socket.socket: Objeto socket configurado en modo no bloqueante.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, puerto))
    sock.setblocking(False)
    return sock


def procesar_datos(data: bytes, umbral: float) -> bytes:
    """
    Procesa los datos recibidos y determina el comando a enviar al Arduino.

    Args:
        data (bytes): Datos UDP recibidos (ej. "0.5,-1.0").
        umbral (float): Valor mínimo para considerar un movimiento.

    Returns:
        bytes: Comando a enviar por serial ('W', 'S', 'A', 'D' o 'X').
    """
    try:
        x_str, y_str = data.decode().strip().split(",")
        eje_x, eje_y = float(x_str), float(y_str)

        if eje_y < -umbral:
            return b'W'  # Adelante
        elif eje_y > umbral:
            return b'S'  # Atrás
        elif eje_x < -umbral:
            return b'A'  # Izquierda
        elif eje_x > umbral:
            return b'D'  # Derecha
        else:
            return b'X'  # Detener
    except Exception:
        return b'X'  # Por seguridad, detiene si hay error


def main():
    """
    Bucle principal que escucha comandos UDP y controla
    el Arduino en tiempo real.
    """
    UMBRAL = 0.9
    TIMEOUT = 0.3  # 300 ms
    arduino = inicializar_arduino()
    sock = configurar_socket_udp()
    last_received = time.time()

    print("Esperando comandos UDP (baja latencia)... Ctrl+C para salir")

    try:
        while True:
            try:
                data, _ = sock.recvfrom(1024)
                print(f"{data.decode('utf-8', errors='replace')}")
                comando = procesar_datos(data, UMBRAL)
                arduino.write(comando)
                last_received = time.time()

            except BlockingIOError:
                # Si no hay datos y pasó el tiempo de espera, detener
                if time.time() - last_received > TIMEOUT:
                    arduino.write(b'X')

            time.sleep(0.001)  # Evita uso excesivo de CPU

    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario")

    finally:
        arduino.write(b'X')  # Asegura detención
        arduino.close()
        sock.close()


if __name__ == "__main__":
    main()
