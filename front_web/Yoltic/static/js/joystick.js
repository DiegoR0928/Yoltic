// Establecer la conexión WebSocket
const socket = new WebSocket('ws://localhost:8000/ws/joystick/');

// Mostrar un mensaje cuando la conexión esté establecida
socket.onopen = function(e) {
    console.log("Conexión WebSocket establecida.");
    document.getElementById("joy-status").innerText = "Conexión establecida";
};

// Manejar el cierre de la conexión WebSocket
socket.onclose = function(e) {
    console.log("Conexión WebSocket cerrada.");
    document.getElementById("joy-status").innerText = "Conexión cerrada";
};

// Manejar errores de WebSocket
socket.onerror = function(error) {
    console.log("Error en la conexión WebSocket:", error);
    document.getElementById("joy-status").innerText = "Error en la conexión";
};

// Recibir datos del servidor WebSocket (opcional)
socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const x = data.x;
    const y = data.y;
    document.getElementById("joy-x").innerText = x;
    document.getElementById("joy-y").innerText = y;
};

// Enviar coordenadas simuladas
function sendJoystickData(x, y) {
    if (socket.readyState === WebSocket.OPEN) {
      const data = { 'x': x, 'y': y };
      socket.send(JSON.stringify(data));
    }
}

/* // Simular coordenadas y enviarlas periódicamente
function sendCoordinates() {
    if (socket.readyState === WebSocket.OPEN) {
        const x = (Math.random() * 2 - 1).toFixed(2);  // entre -1.00 y 1.00
        const y = (Math.random() * 2 - 1).toFixed(2);
        sendJoystickData(x, y);
    }
    setTimeout(sendCoordinates, 100);  // cada 100 ms
} */


let stick = document.getElementById("stick-left");
let coords = document.getElementById("coords");

function updateGamepad() {
  const UMBRAL = 0.5; // Umbral mínimo para detectar movimiento
  let gamepads = navigator.getGamepads();
  let gp = gamepads[0];

  if (gp) {
    let x = gp.axes[0]; // Eje X del stick izquierdo
    let y = gp.axes[1]; // Eje Y del stick izquierdo

    // Mostrar coordenadas en el HTML siempre, si quieres ver la salida en pantalla
    coords.textContent = `X: ${x.toFixed(2)}, Y: ${y.toFixed(2)}`;

    // Solo enviar si se supera el umbral
    if (Math.abs(x) > UMBRAL || Math.abs(y) > UMBRAL) {
      let max = 20;
      stick.style.transform = `translate(${x * max}px, ${y * max}px)`;
      sendJoystickData(x, y); // Enviar al servidor solo si hay movimiento real
    } else {
      // Opcional: volver a centrar el stick visual si está en reposo
      stick.style.transform = `translate(0px, 0px)`;
    }
  }

  requestAnimationFrame(updateGamepad);
}

window.addEventListener("gamepadconnected", (e) => {
  console.log("Gamepad conectado:", e.gamepad);
  requestAnimationFrame(updateGamepad);
});

window.addEventListener("gamepaddisconnected", (e) => {
  console.log("Gamepad desconectado:", e.gamepad);
});