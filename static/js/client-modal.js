/**
 * LEMON POS - Client Modal Functions
 * Manejo del modal de selección/creación de clientes
 */

// Funciones del Modal de Clientes
function openClientModal() {
    document.getElementById('clientModal').classList.remove('hidden');
    document.body.style.overflow = 'hidden';

    // Cargar todos los clientes al abrir
    loadAllClients();

    // Focus en el buscador
    setTimeout(() => {
        document.getElementById('modal-client-search').focus();
    }, 100);
}

function loadAllClients() {
    const listContainer = document.getElementById('modal-clients-list');
    listContainer.innerHTML = `
        <div class="text-center py-12 text-gray-500">
            <i class="fas fa-spinner fa-spin text-4xl mb-3 text-emerald-500"></i>
            <p>Cargando clientes...</p>
        </div>
    `;

    fetch(`${window.DJANGO_VARS.searchClientsUrl}?q=`)
        .then(response => response.json())
        .then(clients => {
            if (clients.length === 0) {
                listContainer.innerHTML = `
                    <div class="text-center py-12 text-gray-500">
                        <i class="fas fa-user-slash text-4xl mb-3 text-gray-300"></i>
                        <p class="text-lg font-semibold mb-2">No hay clientes registrados</p>
                        <p class="text-sm">Crea tu primer cliente usando el botón "Crear Nuevo"</p>
                    </div>
                `;
                return;
            }

            listContainer.innerHTML = clients.map(client => `
                <div class="client-item bg-white border-2 border-gray-200 rounded-xl p-4 hover:border-emerald-500" 
                     onclick="selectClient(${client.id}, '${client.nombre}', '${client.identificacion}')">
                    <div class="flex items-center gap-4">
                        <div class="w-12 h-12 bg-gradient-to-br from-emerald-100 to-lime-100 rounded-xl flex items-center justify-center text-emerald-700 font-bold text-lg">
                            ${client.nombre.charAt(0).toUpperCase()}
                        </div>
                        <div class="flex-1">
                            <h3 class="font-bold text-gray-900 text-lg">${client.nombre}</h3>
                            <p class="text-gray-600 text-sm">
                                <i class="fas fa-id-card mr-1"></i>${client.identificacion}
                                ${client.telefono ? `<span class="ml-3"><i class="fas fa-phone mr-1"></i>${client.telefono}</span>` : ''}
                            </p>
                        </div>
                        <i class="fas fa-chevron-right text-gray-400"></i>
                    </div>
                </div>
            `).join('');
        })
        .catch(error => {
            console.error('Error cargando clientes:', error);
            listContainer.innerHTML = `
                <div class="text-center py-12 text-red-500">
                    <i class="fas fa-exclamation-triangle text-4xl mb-3"></i>
                    <p>Error al cargar clientes</p>
                </div>
            `;
        });
}

function closeClientModal(event) {
    if (!event || event.target.id === 'clientModal' || event.type === 'click') {
        document.getElementById('clientModal').classList.add('hidden');
        document.body.style.overflow = 'auto';
    }
}

function switchClientTab(tab) {
    // Actualizar tabs
    document.querySelectorAll('.client-tab').forEach(t => {
        t.classList.remove('active', 'text-emerald-600', 'border-b-2', 'border-emerald-500');
        t.classList.add('text-gray-600');
    });

    const activeTab = document.getElementById(`tab-${tab}`);
    activeTab.classList.add('active', 'text-emerald-600', 'border-b-2', 'border-emerald-500');
    activeTab.classList.remove('text-gray-600');

    // Mostrar contenido
    document.querySelectorAll('.client-tab-content').forEach(c => c.classList.add('hidden'));
    document.getElementById(`${tab}-client-tab`).classList.remove('hidden');
}

let searchTimeout;
function searchClientsInModal(query) {
    clearTimeout(searchTimeout);

    // Si está vacío, cargar todos los clientes
    if (query.length === 0) {
        loadAllClients();
        return;
    }

    if (query.length < 2) {
        document.getElementById('modal-clients-list').innerHTML = `
            <div class="text-center py-12 text-gray-500">
                <i class="fas fa-search text-4xl mb-3 text-gray-300"></i>
                <p>Escribe al menos 2 caracteres para buscar...</p>
            </div>
        `;
        return;
    }

    searchTimeout = setTimeout(() => {
        fetch(`${window.DJANGO_VARS.searchClientsUrl}?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(clients => {
                const listContainer = document.getElementById('modal-clients-list');

                if (clients.length === 0) {
                    listContainer.innerHTML = `
                        <div class="text-center py-12 text-gray-500">
                            <i class="fas fa-user-slash text-4xl mb-3 text-gray-300"></i>
                            <p class="text-lg font-semibold mb-2">No se encontraron clientes</p>
                            <p class="text-sm">Intenta con otro término o crea un nuevo cliente</p>
                        </div>
                    `;
                    return;
                }

                listContainer.innerHTML = clients.map(client => `
                    <div class="client-item bg-white border-2 border-gray-200 rounded-xl p-4 hover:border-emerald-500" 
                         onclick="selectClient(${client.id}, '${client.nombre}', '${client.identificacion}')">
                        <div class="flex items-center gap-4">
                            <div class="w-12 h-12 bg-gradient-to-br from-emerald-100 to-lime-100 rounded-xl flex items-center justify-center text-emerald-700 font-bold text-lg">
                                ${client.nombre.charAt(0).toUpperCase()}
                            </div>
                            <div class="flex-1">
                                <h3 class="font-bold text-gray-900 text-lg">${client.nombre}</h3>
                                <p class="text-gray-600 text-sm">
                                    <i class="fas fa-id-card mr-1"></i>${client.identificacion}
                                    ${client.telefono ? `<span class="ml-3"><i class="fas fa-phone mr-1"></i>${client.telefono}</span>` : ''}
                                </p>
                            </div>
                            <i class="fas fa-chevron-right text-gray-400"></i>
                        </div>
                    </div>
                `).join('');
            })
            .catch(error => {
                console.error('Error buscando clientes:', error);
            });
    }, 300);
}

function selectClient(clientId, clientName, clientIdentification) {
    // 🎯 Llamar a la API para aplicar descuentos/recargos del cliente
    const aplicarClienteDescuentosUrl = window.DJANGO_VARS?.aplicarClienteDescuentosUrl;

    console.log('=== SELECT CLIENT ===');
    console.log('URL:', aplicarClienteDescuentosUrl);
    console.log('Cliente ID:', clientId);

    if (!aplicarClienteDescuentosUrl) {
        console.error('URL de aplicar descuentos no encontrada');
        return;
    }

    fetch(aplicarClienteDescuentosUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({
            venta_id: window.DJANGO_VARS?.ventaId,
            cliente_id: clientId
        })
    })
        .then(response => response.json())
        .then(data => {
            console.log('Respuesta:', data);

            if (data.success) {
                // Log de totales para debug
                console.log('Totales recibidos:', data.totales);

                // Actualizar UI con botones
                document.getElementById('customer-display').innerHTML = `
                <div class="flex items-center justify-between gap-3">
                    <div class="flex-1">
                        <div class="text-sm font-bold text-gray-900">${clientName}</div>
                        <div class="text-xs text-gray-600">${clientIdentification}</div>
                    </div>
                    <div class="flex gap-2">
                        <button onclick="openClientModal()" 
                                class="text-xs bg-emerald-500 hover:bg-emerald-600 text-white px-3 py-1.5 rounded-lg font-medium transition-all flex items-center gap-1">
                            <i class="fas fa-edit"></i>Cambiar
                        </button>
                        <button onclick="removeClient()" 
                                class="text-xs bg-red-500 hover:bg-red-600 text-white px-3 py-1.5 rounded-lg font-medium transition-all flex items-center gap-1">
                            <i class="fas fa-times"></i>Quitar
                        </button>
                    </div>
                </div>
            `;

                // Actualizar totales en la UI
                if (data.totales) {
                    const displayTotal = document.getElementById('display-total');
                    const displaySubtotal = document.getElementById('display-subtotal');
                    const displayIva = document.getElementById('display-iva');
                    const cobrarAmount = document.getElementById('cobrar-amount');

                    if (displayTotal) displayTotal.textContent = '$' + data.totales.total.toFixed(2);
                    if (displaySubtotal) displaySubtotal.textContent = '$' + data.totales.subtotal.toFixed(2);
                    if (displayIva) displayIva.textContent = '$' + data.totales.iva.toFixed(2);
                    if (cobrarAmount) cobrarAmount.textContent = '$' + data.totales.total.toFixed(2);

                    // Actualizar variable global totalAmount
                    if (typeof totalAmount !== 'undefined') {
                        totalAmount = data.totales.total;
                    }
                    window.DJANGO_VARS.total = data.totales.total;

                    // Recalcular cambio si hay monto ingresado
                    const cashAmountInput = document.getElementById('cash_amount');
                    if (cashAmountInput && cashAmountInput.value) {
                        // Trigger recalculation
                        cashAmountInput.dispatchEvent(new Event('input'));
                    }

                    // Limpiar monto recibido y cambio
                    if (cashAmountInput) {
                        cashAmountInput.value = '';
                    }
                    const cashChangeInput = document.getElementById('cash_change');
                    if (cashChangeInput) {
                        cashChangeInput.value = '';
                    }

                    // Mostrar/ocultar descuento
                    const descuentoRow = document.getElementById('descuento-row');
                    if (descuentoRow) {
                        if (data.totales.descuento_total > 0) {
                            descuentoRow.classList.remove('hidden');
                            const porcentaje = data.cliente && data.cliente.tasa_descuento ? ` (${data.cliente.tasa_descuento.toFixed(1)}%)` : '';
                            document.getElementById('display-descuento').textContent = '-$' + data.totales.descuento_total.toFixed(2) + porcentaje;
                        } else {
                            descuentoRow.classList.add('hidden');
                        }
                    }

                    // Mostrar/ocultar recargo
                    const recargoRow = document.getElementById('recargo-row');
                    if (recargoRow) {
                        if (data.totales.recargo_total > 0) {
                            recargoRow.classList.remove('hidden');
                            const porcentaje = data.cliente && data.cliente.tasa_recargo ? ` (${data.cliente.tasa_recargo.toFixed(1)}%)` : '';
                            document.getElementById('display-recargo').textContent = '+$' + data.totales.recargo_total.toFixed(2) + porcentaje;
                        } else {
                            recargoRow.classList.add('hidden');
                        }
                    }
                }

                // Cerrar modal
                closeClientModal();

                // 🎯 Actualizar información del cliente y opción de crédito
                if (data.cliente) {
                    console.log('Datos del cliente:', data.cliente);

                    // Habilitar/deshabilitar opción de crédito
                    const creditOption = document.getElementById('credit-payment-option');
                    const creditRadio = document.getElementById('credit');
                    const creditInfo = document.getElementById('credit-info');
                    const creditWarning = document.getElementById('credit-warning');
                    const creditIcon = document.getElementById('credit-icon');
                    const creditIconBtn = document.getElementById('credit-icon-btn');
                    const creditTitle = document.getElementById('credit-title');

                    if (creditOption && creditRadio) {
                        if (data.cliente.puede_credito) {
                            // Cliente CON crédito - Verde y habilitado
                            creditOption.classList.remove('opacity-50', 'cursor-not-allowed', 'bg-gray-50', 'border-gray-200', 'bg-yellow-50', 'border-yellow-300', 'hover:border-yellow-500', 'hover:bg-yellow-100');
                            creditOption.classList.add('bg-emerald-50', 'border-emerald-300', 'hover:border-emerald-500', 'hover:bg-emerald-100');
                            creditRadio.disabled = false;

                            if (creditIconBtn) {
                                creditIconBtn.classList.remove('text-gray-400', 'text-yellow-600');
                                creditIconBtn.classList.add('text-emerald-600');
                            }

                            if (creditInfo) {
                                creditInfo.textContent = 'Disponible: ' + data.cliente.credito_dias + ' días, Cupo: $' + data.cliente.cupo.toFixed(2);
                                creditInfo.classList.remove('text-gray-500', 'text-yellow-700');
                                creditInfo.classList.add('text-emerald-700', 'font-semibold');
                            }

                            // Actualizar el warning box
                            if (creditWarning) {
                                creditWarning.classList.remove('bg-yellow-50', 'border-yellow-400', 'bg-red-50', 'border-red-400');
                                creditWarning.classList.add('bg-emerald-50', 'border-emerald-400');
                            }
                            if (creditIcon) {
                                creditIcon.setAttribute('data-lucide', 'check-circle');
                                creditIcon.classList.remove('text-yellow-600', 'text-red-600');
                                creditIcon.classList.add('text-emerald-600');
                            }
                            if (creditTitle) {
                                creditTitle.classList.remove('text-yellow-800', 'text-red-800');
                                creditTitle.classList.add('text-emerald-800');
                            }

                            console.log('✅ Crédito habilitado para', data.cliente.nombre);
                        } else {
                            // Cliente SIN crédito suficiente - Mostrar con ADVERTENCIA
                            console.log('⚠️ Cliente SIN crédito suficiente - Mostrando advertencia');
                            creditOption.classList.remove('opacity-50', 'cursor-not-allowed', 'bg-gray-50', 'border-gray-200', 'bg-emerald-50', 'border-emerald-300');
                            creditOption.classList.add('bg-yellow-50', 'border-yellow-300', 'hover:border-yellow-500', 'hover:bg-yellow-100');
                            creditRadio.disabled = false; // Permitir seleccionar

                            if (creditIconBtn) {
                                creditIconBtn.classList.remove('text-gray-400', 'text-emerald-600');
                                creditIconBtn.classList.add('text-yellow-600');
                            }

                            // Mensaje descriptivo
                            if (creditInfo) {
                                let mensaje = '';
                                if (data.cliente.estado !== 'Activo') {
                                    mensaje = 'Cliente inactivo';
                                } else if (data.cliente.credito_dias <= 0) {
                                    mensaje = 'Cliente sin crédito habilitado';
                                } else if (data.cliente.cupo <= 0) {
                                    mensaje = 'Sin cupo disponible (Cupo: $0.00)';
                                } else {
                                    mensaje = 'Cupo insuficiente (Disponible: $' + data.cliente.cupo.toFixed(2) + ')';
                                }
                                creditInfo.textContent = mensaje;
                                creditInfo.classList.add('text-yellow-700', 'font-semibold');
                                creditInfo.classList.remove('text-emerald-700', 'text-gray-500');
                            }

                            if (creditWarning) {
                                creditWarning.classList.remove('bg-emerald-50', 'border-emerald-400', 'bg-red-50', 'border-red-400');
                                creditWarning.classList.add('bg-yellow-50', 'border-yellow-400');
                            }
                            if (creditIcon) {
                                creditIcon.setAttribute('data-lucide', 'alert-triangle');
                                creditIcon.classList.remove('text-emerald-600', 'text-red-600');
                                creditIcon.classList.add('text-yellow-600');
                            }
                            if (creditTitle) {
                                creditTitle.classList.remove('text-emerald-800', 'text-red-800');
                                creditTitle.classList.add('text-yellow-800');
                            }

                            console.log('⚠️ Crédito visible con advertencia - sin cupo');
                        }

                        // Re-initialize Lucide icons
                        if (typeof lucide !== 'undefined') {
                            lucide.createIcons();
                        }

                        // Forzar revalidación del botón COBRAR
                        console.log('🔄 Forzando revalidación del botón COBRAR');
                        const creditRadioBtn = document.getElementById('credit');
                        if (creditRadioBtn && creditRadioBtn.checked) {
                            // Si crédito está seleccionado, disparar evento change para revalidar
                            creditRadioBtn.dispatchEvent(new Event('change'));
                        }
                    }
                }

                // Mostrar notificación de éxito
                showNotification('Cliente seleccionado correctamente', 'success');
            } else {
                showNotification('Error: ' + (data.error || 'Error desconocido'), 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error al seleccionar cliente', 'error');
        });
}

function removeClient() {
    // Simplemente recargar la página para restaurar consumidor final
    window.location.reload();
}

function createQuickClient(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData);

    // 🎯 Agregar valores por defecto para campos no presentes
    if (!data.grupo) data.grupo = 'regular';
    if (!data.estado) data.estado = 'activo';
    if (!data.credito) data.credito = '0';
    if (!data.cupo) data.cupo = '0';
    if (!data.tasa_descuento) data.tasa_descuento = '0';
    if (!data.tasa_recargo) data.tasa_recargo = '0';

    // Agregar CSRF token
    data.csrfmiddlewaretoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch(window.DJANGO_VARS.createClientUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams(data)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Seleccionar automáticamente el cliente creado
                selectClient(data.client_id, data.client_name, data.client_identification);
                showNotification('Cliente creado y seleccionado', 'success');
            } else {
                showNotification('Error al crear cliente: ' + (data.error || 'Error desconocido'), 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error al crear cliente', 'error');
        });
}

function showNotification(message, type = 'success') {
    // Crear elemento de notificación
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 px-6 py-4 rounded-xl shadow-2xl transform transition-all duration-300 flex items-center gap-3 ${type === 'success' ? 'bg-emerald-500 text-white' : 'bg-red-500 text-white'
        }`;
    notification.style.transform = 'translateX(400px)';

    notification.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'} text-xl"></i>
        <span class="font-semibold">${message}</span>
    `;

    document.body.appendChild(notification);

    // Animar entrada
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 10);

    // Remover después de 3 segundos
    setTimeout(() => {
        notification.style.transform = 'translateX(400px)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Cerrar modal con ESC
document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
        closeClientModal();
    }
});
