// Función para manejar el botón de inicio
async function startRecording() {
    const btn = document.getElementById('btn-iniciar');
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Iniciando...';
    
    try {
        const response = await fetch('/comenzar-grabacion-todas/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Error al iniciar grabación');
        }
        
        // Mostrar resultados por cámara
        let message = 'Grabación iniciada: ';
        for (const [cam, status] of Object.entries(data.results)) {
            message += `Cámara ${cam}: ${status === 'success' ? '✅' : '❌'} `;
        }
        
        showAlert(message, data.status === 'error' ? 'danger' : 'warning');
        
    } catch (error) {
        console.error('Error:', error);
        showAlert(error.message, 'danger');
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

// Función para manejar el botón de detener
async function stopRecording() {
    const btn = document.getElementById('btn-detener');
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Deteniendo...';
    
    try {
        const response = await fetch('/detener-grabacion-todas/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Error al detener grabación');
        }
        
        showAlert('Grabación detenida correctamente', 'success');
        
    } catch (error) {
        console.error('Error:', error);
        showAlert(error.message, 'danger');
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

// Función auxiliar para mostrar alertas
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
    alertDiv.style.zIndex = '1000';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
    
    // Auto-eliminar después de 5 segundos
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Asignar eventos
document.getElementById('btn-iniciar').addEventListener('click', startRecording);
document.getElementById('btn-detener').addEventListener('click', stopRecording);
