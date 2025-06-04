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
    3: "https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/720/Big_Buck_Bunny_720_10s_1MB.mp4"
  };

  const html = `
    <div class="col-md-12 camera-box d-flex justify-content-center align-items-center" style="height: 100vh;">
      <img src="${urls[camId]}" width="1280" height="720"/>
    </div>
    <button id="btn-volver" class="btn btn-primary" onclick="mostrarTresCamaras()">Volver</button>
    <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
    <button id="btn-iniciar-individual" class="btn btn-primary" data-cam-id="${camId}">Iniciar Grabación</button>
    <button id="btn-detener-individual" class="btn btn-primary" data-cam-id="${camId}">Detener Grabación</button>
    <a id="btn-grabaciones" href="${listaGrabacionesURL}" class="btn btn-secondary">Ver Grabaciones</a>
  `;

  document.getElementById("contenedor-camaras").innerHTML = html;

  document.getElementById('btn-iniciar-individual').addEventListener('click', (event) => {
      const cam_id = event.currentTarget.getAttribute('data-cam-id');
      startRecordingIndividual(cam_id);
  });

  document.getElementById('btn-detener-individual').addEventListener('click', (event) => {
      const cam_id = event.currentTarget.getAttribute('data-cam-id');
      stopRecordingIndividual(cam_id);
  });



  document.getElementById("btn-volver").style.display = "block";

  document.querySelectorAll(".camera-box").forEach(camera => {
    camera.style.display = "none";
  });

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
  contenedor.innerHTML = `
    <div class="col-md-4 camera-box hover">
      <a onclick="mostrarCamara(1); return false;">
        <img src="/mjpeg1/" width="640" height="480"/>
      </a>
    </div>
    <div class="col-md-4 camera-box hover">
      <a onclick="mostrarCamara(2); return false;">
        <img src="/mjpeg2/" width="640" height="480"/>
      </a>
    </div>
    <div class="col-md-4 camera-box hover">
      <a onclick="mostrarCamara(3); return false;">
        <img src="/mjpeg3/" width="640" height="480"/>
      </a>
    </div>
    <button id="btn-volver" class="btn btn-primary" onclick="mostrarTresCamaras()">Volver</button>
    <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
    <button id="btn-iniciar" class="btn btn-primary">Iniciar Grabación</button>
    <button id="btn-detener" class="btn btn-primary">Detener Grabación</button>
    <a id="btn-grabaciones" href="${listaGrabacionesURL}" class="btn btn-secondary">Ver Grabaciones</a>
  `;

  // Ocultar el botón de volver
  document.getElementById("btn-volver").style.display = "none";

  document.getElementById('btn-iniciar').addEventListener('click', startRecording);
  document.getElementById('btn-detener').addEventListener('click', stopRecording);

  // Mostrar las cámaras pequeñas
  document.querySelectorAll(".camera-box").forEach(camera => {
    camera.style.display = "block";
  });
}
