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

  // Ocultar las tres cámaras
  document.querySelectorAll(".camera-box").forEach(camera => {
    camera.style.display = "none";
  });

    document.getElementById("contenedor-camaras").innerHTML = html;
  }

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

  // Mostrar las cámaras
  document.querySelectorAll(".camera-box").forEach(camera => {
    camera.style.display = "block";
  });
}

