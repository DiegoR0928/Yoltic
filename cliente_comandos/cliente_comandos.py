import serial
import socket
import time

# Configuración Arduino
# El COM4, es la entrada por la que entra el serial al arduino
# Hay que instalar los drivers del arduino a la PC Correspondiente
arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2)  # Espera inicial para estabilizar la conexión

# Configuración UDP
UDP_IP = "0.0.0.0"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.setblocking(False)  # Usamos non-blocking en lugar de timeout

UMBRAL = 0.9
TIMEOUT = 0.3  # 300 ms sin datos para detener
last_received = time.time()

print("Esperando comandos UDP (baja latencia)... Ctrl+C para salir")

try:
    while True:
        try:
            data, _ = sock.recvfrom(1024)
            print(f"{data.decode('utf-8', errors='replace')}")
            last_received = time.time()

            # Procesamiento rápido
            x_str, y_str = data.decode().strip().split(",")
            eje_x, eje_y = float(x_str), float(y_str)

            if eje_y < -UMBRAL:
                arduino.write(b'W')
            elif eje_y > UMBRAL:
                arduino.write(b'S')
            elif eje_x < -UMBRAL:
                arduino.write(b'A')
            elif eje_x > UMBRAL:
                arduino.write(b'D')
            else:
                arduino.write(b'X')

        except BlockingIOError:
            # No hay datos disponibles
            if time.time() - last_received > TIMEOUT:
                arduino.write(b'X')

        except ValueError:
            pass  # Ignorar errores de formato
        except UnicodeDecodeError:
            pass  # Ignorar errores de decodificación

        # Pequeña pausa para no saturar la CPU
        time.sleep(0.001)

except KeyboardInterrupt:
    print("\nInterrumpido por el usuario")
finally:
    arduino.write(b'X')  # Asegurar detención
    arduino.close()
    sock.close()

