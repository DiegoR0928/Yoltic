// Establecer la conexión WebSocket
const socket = new WebSocket('ws://localhost:8000/ws/joystick/');

// Recibir datos del servidor WebSocket (opcional)
socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const x = data.x;
    const y = data.y;
    document.getElementById("joy-x").innerText = x;
    document.getElementById("joy-y").innerText = y;
};

function sendJoystickData(x, y) {
    if (socket.readyState === WebSocket.OPEN) {
        const data = { 'x': x, 'y': y };
        socket.send(JSON.stringify(data));
    }
}

let stick = document.getElementById("stick-left");
let coords = document.getElementById("coords");
let status = document.getElementById("joy-status");

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

window.addEventListener("gamepadconnected", (e) => {
    console.log("Gamepad conectado:", e.gamepad);

    // Hacemos una lectura inicial forzada para que se actualice de inmediato
    const gp = navigator.getGamepads()[e.gamepad.index];
    if (gp) {
        document.getElementById("joy-status").innerText = "Gamepad conectado ✅";
        document.getElementById("coords").textContent = `X: ${gp.axes[0].toFixed(2)}, Y: ${gp.axes[1].toFixed(2)}`;
    }

    // Comenzar animación continua
    requestAnimationFrame(updateGamepad);
});

window.addEventListener("gamepaddisconnected", (e) => {
    console.log("Gamepad desconectado:", e.gamepad);
    document.getElementById("joy-status").innerText = "Gamepad conectado ❌";
    document.getElementById("coords").textContent = `X: 0, Y: 0`;
});

