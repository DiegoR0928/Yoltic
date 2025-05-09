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
    const data = { 'x': x, 'y': y };
    socket.send(JSON.stringify(data));
    // Mostrar también en la interfaz local
    document.getElementById("joy-x").innerText = x;
    document.getElementById("joy-y").innerText = y;
}

// Simular coordenadas y enviarlas periódicamente
function sendCoordinates() {
    if (socket.readyState === WebSocket.OPEN) {
        const x = (Math.random() * 2 - 1).toFixed(2);  // entre -1.00 y 1.00
        const y = (Math.random() * 2 - 1).toFixed(2);
        sendJoystickData(x, y);
    }
    setTimeout(sendCoordinates, 100);  // cada 100 ms
}

// Iniciar
sendCoordinates();