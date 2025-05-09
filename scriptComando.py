import socket

# Configuración del socket
IP_LOCAL = "0.0.0.0"  # Escucha en todas las interfaces de red
PUERTO = 5005    # Puerto donde se recibirán los paquetes

# Crear el socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP_LOCAL, PUERTO))

print(f"Escuchando UDP en {IP_LOCAL}:{PUERTO}...")

try:
    while True:
        datos, direccion = sock.recvfrom(1024)  # Tamaño máximo del paquete: 1024 bytes
        print(f"Recibido de {direccion}: {datos.decode('utf-8', errors='replace')}")
except KeyboardInterrupt:
    print("\nRecepción terminada por el usuario.")
finally:
    sock.close()