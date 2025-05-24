/**
 * Establece la conexión WebSocket con el servidor para enviar y recibir datos del joystick.
 */
const socket = new WebSocket('ws://localhost:8000/ws/joystick/');

/**
 * Manejador para recibir mensajes del servidor WebSocket.
 *
 * Args:
 *   e (MessageEvent): Evento que contiene los datos recibidos.
 *
 * Returns:
 *   void
 */
socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const x = data.x;
    const y = data.y;
    document.getElementById("joy-x").innerText = x;
    document.getElementById("joy-y").innerText = y;
};

/**
 * Envía las coordenadas del joystick al servidor mediante WebSocket.
 *
 * Args:
 *   x (number): Posición horizontal del joystick.
 *   y (number): Posición vertical del joystick.
 *
 * Returns:
 *   void
 */
function sendJoystickData(x, y) {
    if (socket.readyState === WebSocket.OPEN) {
        const data = { 'x': x, 'y': y };
        socket.send(JSON.stringify(data));
    }
}

// Referencias a elementos DOM para actualizar interfaz
let stick = document.getElementById("stick-left");
let coords = document.getElementById("coords");
let status = document.getElementById("joy-status");

/**
 * Actualiza continuamente la posición del joystick detectado por la API Gamepad.
 * Si el movimiento supera un umbral, mueve el elemento visual y envía datos por WebSocket.
 *
 * Args:
 *   Ninguno.
 *
 * Returns:
 *   void
 */
function updateGamepad() {
    const UMBRAL = 0.5;
    let gamepads = navigator.getGamepads();
    let gp = gamepads[0];

    if (gp) {
        let x = gp.axes[0];
        let y = gp.axes[1];

        coords.textContent = `X: ${x.toFixed(2)}, Y: ${y.toFixed(2)}`;

        if (Math.abs(x) > UMBRAL || Math.abs(y) > UMBRAL) {
            let max = 20;
            stick.style.transform = `translate(${x * max}px, ${y * max}px)`;
            sendJoystickData(x, y);
        } else {
            stick.style.transform = `translate(0px, 0px)`;
        }
    }

    requestAnimationFrame(updateGamepad);
}

/**
 * Evento que se dispara cuando un gamepad es conectado.
 * Actualiza el estado en pantalla e inicia la actualización continua.
 *
 * Args:
 *   e (GamepadEvent): Evento con información del gamepad conectado.
 *
 * Returns:
 *   void
 */
window.addEventListener("gamepadconnected", (e) => {
    console.log("Gamepad conectado:", e.gamepad);

    // Lectura inicial para actualizar inmediatamente
    const gp = navigator.getGamepads()[e.gamepad.index];
    if (gp) {
        document.getElementById("joy-status").innerText = "Gamepad conectado ✅";
        document.getElementById("coords").textContent = `X: ${gp.axes[0].toFixed(2)}, Y: ${gp.axes[1].toFixed(2)}`;
    }

    // Inicia animación para actualización continua
    requestAnimationFrame(updateGamepad);
});

/**
 * Evento que se dispara cuando un gamepad es desconectado.
 * Actualiza el estado en pantalla para reflejar desconexión.
 *
 * Args:
 *   e (GamepadEvent): Evento con información del gamepad desconectado.
 *
 * Returns:
 *   void
 */
window.addEventListener("gamepaddisconnected", (e) => {
    console.log("Gamepad desconectado:", e.gamepad);
    document.getElementById("joy-status").innerText = "Gamepad desconectado ❌";
    document.getElementById("coords").textContent = `X: 0, Y: 0`;
});
