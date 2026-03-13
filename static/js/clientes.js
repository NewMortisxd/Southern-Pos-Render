/**
 * LEMON POS - JavaScript para Clientes
 * Funcionalidades para gestión de clientes
 */

// Función para obtener el token CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Marca o desmarca un cliente como favorito
 * @param {number} clienteId - ID del cliente
 * @param {HTMLElement} element - Elemento del icono de estrella
 */
function toggleFavorito(clienteId, element) {
    const csrftoken = getCookie('csrftoken');
    
    fetch(`/clients/toggle-favorito/${clienteId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (data.es_favorito) {
                element.classList.add('active');
                // Animación de éxito
                element.style.transform = 'scale(1.3)';
                setTimeout(() => {
                    element.style.transform = 'scale(1)';
                }, 200);
            } else {
                element.classList.remove('active');
            }
        }
    })
    .catch(error => {
        console.error('Error al marcar favorito:', error);
        // Mostrar mensaje de error si existe un sistema de notificaciones
        if (typeof showNotification === 'function') {
            showNotification('Error al actualizar favorito', 'error');
        }
    });
}

/**
 * Búsqueda de clientes en tiempo real
 * @param {string} searchTerm - Término de búsqueda
 * @param {function} callback - Función callback con los resultados
 */
function searchClients(searchTerm, callback) {
    if (searchTerm.length < 2) {
        callback([]);
        return;
    }
    
    fetch(`/clients/search/?q=${encodeURIComponent(searchTerm)}`)
        .then(response => response.json())
        .then(data => {
            callback(data);
        })
        .catch(error => {
            console.error('Error en búsqueda de clientes:', error);
            callback([]);
        });
}

/**
 * Inicializa el autocompletado de búsqueda de clientes
 * @param {string} inputId - ID del input de búsqueda
 * @param {string} resultsId - ID del contenedor de resultados
 */
function initClientSearch(inputId, resultsId) {
    const input = document.getElementById(inputId);
    const resultsContainer = document.getElementById(resultsId);
    
    if (!input || !resultsContainer) return;
    
    let debounceTimer;
    
    input.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        
        debounceTimer = setTimeout(() => {
            const searchTerm = this.value.trim();
            
            searchClients(searchTerm, (results) => {
                displaySearchResults(results, resultsContainer);
            });
        }, 300);
    });
    
    // Cerrar resultados al hacer click fuera
    document.addEventListener('click', function(e) {
        if (!input.contains(e.target) && !resultsContainer.contains(e.target)) {
            resultsContainer.innerHTML = '';
            resultsContainer.style.display = 'none';
        }
    });
}

/**
 * Muestra los resultados de búsqueda
 * @param {Array} results - Array de resultados
 * @param {HTMLElement} container - Contenedor de resultados
 */
function displaySearchResults(results, container) {
    if (results.length === 0) {
        container.style.display = 'none';
        return;
    }
    
    container.innerHTML = '';
    container.style.display = 'block';
    
    results.forEach(client => {
        const item = document.createElement('div');
        item.className = 'search-result-item';
        item.innerHTML = `
            <div class="flex items-center gap-3 p-3 hover:bg-gray-50 cursor-pointer rounded-lg">
                <div class="client-avatar" style="background: #dbeafe; color: #1e40af;">
                    ${getInitials(client.nombre)}
                </div>
                <div class="flex-1">
                    <div class="font-semibold text-gray-900">${client.nombre}</div>
                    <div class="text-sm text-gray-500">${client.identificacion}</div>
                </div>
            </div>
        `;
        
        item.addEventListener('click', () => {
            selectClient(client);
            container.style.display = 'none';
        });
        
        container.appendChild(item);
    });
}

/**
 * Obtiene las iniciales de un nombre
 * @param {string} nombre - Nombre completo
 * @returns {string} Iniciales
 */
function getInitials(nombre) {
    const palabras = nombre.split(' ');
    if (palabras.length >= 2) {
        return `${palabras[0][0]}${palabras[1][0]}`.toUpperCase();
    } else if (palabras.length === 1) {
        return palabras[0].substring(0, 2).toUpperCase();
    }
    return 'CL';
}

/**
 * Selecciona un cliente (implementar según necesidad)
 * @param {Object} client - Objeto del cliente
 */
function selectClient(client) {
    // Esta función debe ser implementada según el contexto
    // Por ejemplo, en un formulario de venta, llenar los datos del cliente
    console.log('Cliente seleccionado:', client);
}

/**
 * Confirma la eliminación de un cliente
 * @param {string} clientName - Nombre del cliente
 * @param {string} deleteUrl - URL para eliminar
 */
function confirmDeleteClient(clientName, deleteUrl) {
    if (confirm(`¿Estás seguro de eliminar al cliente "${clientName}"?\n\nEsta acción no se puede deshacer.`)) {
        window.location.href = deleteUrl;
    }
}

/**
 * Exporta la lista de clientes a CSV
 */
function exportClientsToCSV() {
    // Obtener todos los clientes visibles en la tabla
    const rows = document.querySelectorAll('.client-row');
    let csv = 'Nombre,Identificación,Teléfono,Email,Grupo,Estado\n';
    
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length > 0) {
            const nombre = cells[1].querySelector('.font-semibold')?.textContent || '';
            const identificacion = cells[1].querySelector('.text-sm')?.textContent || '';
            const telefono = cells[2].textContent.trim();
            const email = cells[3].textContent.trim();
            const grupo = cells[4].textContent.trim();
            const estado = cells[7].textContent.trim();
            
            csv += `"${nombre}","${identificacion}","${telefono}","${email}","${grupo}","${estado}"\n`;
        }
    });
    
    // Crear y descargar el archivo
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', `clientes_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Filtra clientes por grupo
 * @param {string} grupo - Grupo a filtrar
 */
function filterByGroup(grupo) {
    const rows = document.querySelectorAll('.client-row');
    
    rows.forEach(row => {
        const grupoCell = row.querySelector('td:nth-child(5)');
        if (grupoCell) {
            const grupoText = grupoCell.textContent.trim().toLowerCase();
            if (grupo === 'todos' || grupoText.includes(grupo.toLowerCase())) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        }
    });
}

/**
 * Inicializa tooltips para los botones de acción
 */
function initActionTooltips() {
    const actionButtons = document.querySelectorAll('.action-btn');
    
    actionButtons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            const title = this.getAttribute('title');
            if (title) {
                // Crear tooltip si no existe
                let tooltip = this.querySelector('.tooltip');
                if (!tooltip) {
                    tooltip = document.createElement('div');
                    tooltip.className = 'tooltip';
                    tooltip.textContent = title;
                    this.appendChild(tooltip);
                }
            }
        });
    });
}

// Inicialización cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips
    initActionTooltips();
    
    // Agregar animaciones suaves a las métricas
    const metricCards = document.querySelectorAll('.metric-card');
    metricCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
});
