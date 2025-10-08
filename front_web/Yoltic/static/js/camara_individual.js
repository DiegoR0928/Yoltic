/**
 * Muestra la cámara seleccionada en tamaño grande y oculta las otras.
 *
 * Args:
 *   camId (number): El ID de la cámara a mostrar (1, 2 o 3).
 *
 * Returns:
 *   void
 */
function mostrarCamara(camId) {
  const urls = {
    1: "/mjpeg1/",
    2: "/mjpeg2/",
    3: "/mjpeg3/"
  };

  // Ocultar panel de control superior
  document.getElementById("control-panel").style.display = "none";

  const contenedor = document.getElementById("contenedor-camaras");
  contenedor.innerHTML = `
    <div class="individual-camera-wrapper" style="display: flex; flex-direction: column; align-items: center; height: calc(100vh - 20px); gap: 10px;">
      
      <div class="camera-card" style="flex: 1; width: 95%; max-width: 1600px; display: flex; flex-direction: column; margin-top: 40px;">
        <div class="camera-header">
          <span>Cámara ${camId}</span>
          <span class="camera-status online">En línea</span>
        </div>
        <div class="camera-feed" style="flex: 1;">
          <img src="${urls[camId]}" class="video-feed" style="width: 100%; height: 100%; object-fit: cover;"/>
        </div>
      </div>

      <div class="d-flex gap-2">
        <button id="btn-iniciar-individual" class="btn btn-tactical" data-cam-id="${camId}">
          <i class="bi bi-record-circle"></i> Iniciar Grabación
        </button>
        <button id="btn-detener-individual" class="btn btn-tactical" data-cam-id="${camId}">
          <i class="bi bi-stop-circle"></i> Detener Grabación
        </button>
        <a id="btn-grabaciones" href="${listaGrabacionesURL}" class="btn btn-tactical-secondary">
          <i class="bi bi-collection-play"></i> Ver Grabaciones
        </a>
        <button id="btn-volver" class="btn btn-danger">Volver</button>
      </div>
    </div>
  `;

  // Eventos de grabación
  document.getElementById('btn-iniciar-individual').addEventListener('click', e => {
    startRecordingIndividual(e.currentTarget.dataset.camId);
  });
  document.getElementById('btn-detener-individual').addEventListener('click', e => {
    stopRecordingIndividual(e.currentTarget.dataset.camId);
  });

  // Volver a las tres cámaras
  document.getElementById('btn-volver').addEventListener('click', () => {
    mostrarTresCamaras();
    document.getElementById("control-panel").style.display = "block";
  });
  
  document.getElementById("control-panel").style.display = "none";
}

/**
 * Muestra las tres cámaras pequeñas en la pantalla principal.
 *
 * Args:
 *   Ninguno.
 *
 * Returns:
 *   void
 */
function mostrarTresCamaras() {
  const contenedor = document.getElementById("contenedor-camaras");

  // Solo reemplazamos el contenido de las cámaras, sin tocar el panel de control
  contenedor.innerHTML = `
    <div class="camera-card">
      <div class="camera-header">
        <span>Cámara 1</span>
        <span class="camera-status online">En línea</span>
      </div>
      <div class="camera-feed hover" onclick="mostrarCamara(1)">
        <img id="cam1-img" data-src="/mjpeg1/" src="/mjpeg1/" class="video-feed" />
      </div>
    </div>

    <div class="camera-card">
      <div class="camera-header">
        <span>Cámara 2</span>
        <span class="camera-status online">En línea</span>
      </div>
      <div class="camera-feed hover" onclick="mostrarCamara(2)">
        <img id="cam2-img" data-src="/mjpeg2/" src="/mjpeg2/" class="video-feed" />
      </div>
    </div>

    <div class="camera-card">
      <div class="camera-header">
        <span>Cámara 3</span>
        <span class="camera-status online">En línea</span>
      </div>
      <div class="camera-feed hover" onclick="mostrarCamara(3)">
        <img id="cam3-img" data-src="/mjpeg3/" src="/mjpeg3/" class="video-feed" />
      </div>
    </div>
  `;

  // Reactivar botones del panel original si es necesario
  document.getElementById('btn-iniciar').disabled = false;
  document.getElementById('btn-detener').disabled = true;

  // Volver a inicializar event listeners para grabación
  document.getElementById('btn-iniciar').addEventListener('click', startRecording);
  document.getElementById('btn-detener').addEventListener('click', stopRecording);
}
