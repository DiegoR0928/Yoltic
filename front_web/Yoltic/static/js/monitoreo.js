 const ws = new WebSocket('ws://' + window.location.host + '/ws/monitoreo/');

  ws.onopen = () => {
    console.log('WebSocket conectado');
  };

  ws.onmessage = (event) => {
    console.log('Mensaje recibido:', event.data);
    const data = JSON.parse(event.data);
    document.getElementById('cpu').textContent = data.cpu;
    document.getElementById('disco').textContent = data.disco;
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };

  ws.onclose = () => {
    console.log('WebSocket cerrado');
  };
