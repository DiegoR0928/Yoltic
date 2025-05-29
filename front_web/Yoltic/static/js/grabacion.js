/**
 * Maneja la acción de iniciar la grabación para todas las cámaras.
 *
 * Deshabilita el botón, muestra un spinner mientras se procesa la petición POST
 * al endpoint '/comenzar-grabacion-todas/', maneja la respuesta y muestra alertas
 * con el resultado.
 *
 * Args:
 *   Ninguno.
 *
 * Returns:
 *   Promise<void>
 */
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

/**
 * Maneja la acción de detener la grabación para todas las cámaras.
 *
 * Deshabilita el botón, muestra un spinner mientras se procesa la petición POST
 * al endpoint '/detener-grabacion-todas/', maneja la respuesta y muestra alertas
 * con el resultado.
 *
 * Args:
 *   Ninguno.
 *
 * Returns:
 *   Promise<void>
 */
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

/**
 * Maneja la acción de iniciar la grabación para una cámara específica.
 *
 * Args:
 *   cam_id (string): ID de la cámara a grabar.
 *
 * Returns:
 *   Promise<void>
 */
async function startRecordingIndividual(cam_id) {
    const btn = document.getElementById('btn-iniciar-individual');
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Iniciando...';

    try {
        const response = await fetch(`/comenzar-grabacion/${cam_id}/`, {
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

        showAlert(data.message, data.status === 'error' ? 'danger' : 'success');
    } catch (error) {
        console.error('Error:', error);
        showAlert(error.message, 'danger');
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

/**
 * Maneja la acción de detener la grabación para una cámara específica.
 *
 * Args:
 *   cam_id (string): ID de la cámara a detener.
 *
 * Returns:
 *   Promise<void>
 */
async function stopRecordingIndividual(cam_id) {
    const btn = document.getElementById('btn-detener-individual');
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Deteniendo...';

    try {
        const response = await fetch(`/detener-grabacion/${cam_id}/`, {
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

        showAlert(data.message, 'success');
    } catch (error) {
        console.error('Error:', error);
        showAlert(error.message, 'danger');
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

/**
 * Muestra una alerta en pantalla con un mensaje y tipo especificado.
 *
 * Crea dinámicamente un div con clases de Bootstrap para alertas, lo agrega
 * al body, y lo elimina automáticamente después de 5 segundos.
 *
 * Args:
 *   message (string): El mensaje que se mostrará en la alerta.
 *   type (string): El tipo de alerta (por ejemplo, 'success', 'danger', 'warning').
 *
 * Returns:
 *   void
 */
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

// Asignar eventos a botones de inicio y detención de grabación para todas las cámaras
document.getElementById('btn-iniciar').addEventListener('click', startRecording);
document.getElementById('btn-detener').addEventListener('click', stopRecording);
