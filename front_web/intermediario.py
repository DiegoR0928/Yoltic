import subprocess
import multiprocessing
import time

# Función para ejecutar el pipeline GStreamer
def start_rtp_to_jpeg_udp(rtp_port, udp_target_port):
    # Definir el pipeline de GStreamer para convertir el RTP a JPEG y enviarlo por UDP
    pipeline = (
        f"gst-launch-1.0 -v "
        f"udpsrc port={rtp_port} caps=application/x-rtp,encoding-name=JPEG,payload=26 ! "
        f"rtpjpegdepay ! jpegdec ! jpegenc ! "
        f"udpsink host=127.0.0.1 port={udp_target_port}"
    )
    
    # Ejecutar el pipeline con subprocess
    subprocess.run(pipeline, shell=True)

# Función para ejecutar todos los pipelines
def run_all_pipelines():
    # Definir los puertos de entrada y salida para cada cámara
    ports = [(5000, 6000), (5001, 6001), (5002, 6002)]
    
    processes = []
    for rtp_port, udp_port in ports:
        # Iniciar cada pipeline en un proceso separado
        p = multiprocessing.Process(target=start_rtp_to_jpeg_udp, args=(rtp_port, udp_port))
        p.start()
        processes.append(p)
    
    # Esperar un segundo antes de continuar
    time.sleep(1)
    
    try:
        # Unir todos los procesos
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        # Manejo de interrupción por teclado para cerrar todos los procesos
        print("Cerrando procesos...")
        for p in processes:
            p.terminate()
        
        # Unir los procesos después de la terminación
        for p in processes:
            p.join()

# Ejecutar la función principal
if __name__ == "__main__":
    run_all_pipelines()

