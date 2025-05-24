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

  const html = `
    <div class="col-md-12 camera-box d-flex justify-content-center align-items-center" style="height: 100vh;">
      <img src="${urls[camId]}" width="640" height="480"/>
    </div>
  `;

  // Mostrar el botón de volver
  document.getElementById("btn-volver").style.display = "block";

  // Ocultar las tres cámaras pequeñas
  document.querySelectorAll(".camera-box").forEach(camera => {
    camera.style.display = "none";
  });

  // Insertar el HTML para la cámara seleccionada
  document.getElementById("contenedor-camaras").innerHTML = html;
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
  `;

  // Ocultar el botón de volver
  document.getElementById("btn-volver").style.display = "none";

  // Mostrar las cámaras pequeñas
  document.querySelectorAll(".camera-box").forEach(camera => {
    camera.style.display = "block";
  });
}
