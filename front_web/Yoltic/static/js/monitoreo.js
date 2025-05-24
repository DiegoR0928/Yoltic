/**
 * Crea una conexión WebSocket con el servidor para recibir datos de monitoreo.
 */
const ws = new WebSocket('ws://' + window.location.host + '/ws/monitoreo/');

/**
 * Evento que se ejecuta cuando la conexión WebSocket se abre correctamente.
 *
 * Args:
 *   Ninguno.
 *
 * Returns:
 *   void
 */
ws.onopen = () => {
  console.log('WebSocket conectado');
};

/**
 * Evento que se ejecuta cuando se recibe un mensaje a través del WebSocket.
 * Actualiza el contenido de los elementos HTML con los datos recibidos.
 *
 * Args:
 *   event (MessageEvent): Evento que contiene el mensaje recibido.
 *
 * Returns:
 *   void
 */
ws.onmessage = (event) => {
  console.log('Mensaje recibido:', event.data);
  const data = JSON.parse(event.data);
  document.getElementById('cpu').textContent = `${data.cpu}%`;
  document.getElementById('disco').textContent = `${data.disco}%`;
};

/**
 * Evento que se ejecuta cuando ocurre un error en la conexión WebSocket.
 *
 * Args:
 *   error (Event): Evento que contiene información del error.
 *
 * Returns:
 *   void
 */
ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

/**
 * Evento que se ejecuta cuando la conexión WebSocket se cierra.
 *
 * Args:
 *   Ninguno.
 *
 * Returns:
 *   void
 */
ws.onclose = () => {
  console.log('WebSocket cerrado');
};
