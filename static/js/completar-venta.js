// Function to get CSRF token from cookies - moved to global scope
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

document.addEventListener('DOMContentLoaded', function () {
    // Make sure Lucide icons are initialized
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }

    // Obtener variables de Django
    let totalAmount = window.DJANGO_VARS?.total || 0;  // Cambiar a let para poder actualizar
    const ventaId = window.DJANGO_VARS?.ventaId || '';
    const verificarStockUrl = window.DJANGO_VARS?.verificarStockUrl || '';
    const actualizarClienteUrl = window.DJANGO_VARS?.actualizarClienteUrl || '';

    // Elementos del DOM
    const cashAmountInput = document.getElementById('cash_amount');
    const cashChangeInput = document.getElementById('cash_change');
    const cashPaymentDetails = document.getElementById('cash-payment-details');
    const cardPaymentDetails = document.getElementById('card-payment-details');
    const registeredCustomerSection = document.getElementById('registered-customer-section');
    const processPaymentBtn = document.getElementById('process-payment');
    const cardNumberInput = document.getElementById('card_number');
    const cardNameInput = document.getElementById('card_name');
    const cardExpiryInput = document.getElementById('card_expiry');
    const cardCvvInput = document.getElementById('card_cvv');
    const metodoPagoInput = document.getElementById('metodo_pago_input');
    const procesarPagoForm = document.getElementById('procesar-pago-form');

    // ============================================
    // LISTENER GLOBAL DE TECLADO - AUTO FOCUS EN MONTO RECIBIDO
    // ============================================
    document.addEventListener('keydown', function (e) {
        // Solo capturar números y punto decimal cuando NO estamos en un input/textarea
        if (e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
            // Números del teclado principal (0-9)
            if ((e.key >= '0' && e.key <= '9') || e.key === '.') {
                e.preventDefault();
                if (cashAmountInput) {
                    // Auto-focus en el input
                    cashAmountInput.focus();
                    // Agregar el número presionado
                    const currentValue = cashAmountInput.value || '';
                    if (e.key === '.' && currentValue.includes('.')) {
                        // No permitir múltiples puntos decimales
                        return;
                    }
                    cashAmountInput.value = currentValue + e.key;
                    // Calcular cambio automáticamente
                    calculateChange();
                }
            }
            // Backspace para borrar
            else if (e.key === 'Backspace') {
                e.preventDefault();
                if (cashAmountInput) {
                    cashAmountInput.focus();
                    const currentValue = cashAmountInput.value || '';
                    cashAmountInput.value = currentValue.slice(0, -1);
                    calculateChange();
                }
            }
        }
    });

    // Agregar evento de submit al formulario para verificar stock antes de procesar
    if (procesarPagoForm) {
        procesarPagoForm.addEventListener('submit', async function (e) {
            e.preventDefault();

            try {
                // Use the getCookie function that's now in global scope
                const csrftoken = getCookie('csrftoken');

                // Verificar stock disponible antes de procesar el pago
                const response = await fetch(verificarStockUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken
                    },
                    body: JSON.stringify({
                        venta_id: ventaId
                    })
                });

                const data = await response.json();

                if (!data.success) {
                    if (data.productos_sin_stock) {
                        // Mostrar alerta con productos sin stock suficiente
                        alert(`Error: No hay suficiente stock para los siguientes productos:\n${data.productos_sin_stock.join('\n')}`);
                    } else if (data.error) {
                        alert(`Error: ${data.error}`);
                    } else {
                        alert('Error desconocido al verificar el stock.');
                    }
                    return;
                }

                // Si hay stock suficiente, enviar el formulario
                this.submit();
            } catch (error) {
                console.error('Error al verificar stock:', error);
                alert('Ocurrió un error al verificar el stock. Por favor, inténtelo de nuevo.');
            }
        });
    }

    // Actualizar método de pago en el formulario
    document.querySelectorAll('input[name="metodo_pago"]').forEach(radio => {
        radio.addEventListener('change', function () {
            if (this.checked) {
                metodoPagoInput.value = this.value;
                document.querySelectorAll('.payment-method').forEach(m => m.classList.remove('active'));
                this.closest('.payment-method').classList.add('active');

                // Manejar visibilidad de secciones según método de pago
                if (cardPaymentDetails && cashPaymentDetails) {
                    cardPaymentDetails.classList.toggle('hidden', this.value !== 'card');
                    cashPaymentDetails.classList.toggle('hidden', this.value !== 'cash');
                }

                // Manejar advertencia de crédito
                const creditWarning = document.getElementById('credit-warning');
                if (creditWarning) {
                    creditWarning.classList.toggle('hidden', this.value !== 'credit');
                }

                // Si es crédito, validar que haya cliente seleccionado
                if (this.value === 'credit') {
                    const clienteIdInput = document.getElementById('cliente_id_input');
                    if (!clienteIdInput || !clienteIdInput.value) {
                        alert('Debe seleccionar un cliente para ventas a crédito');
                        // Volver a efectivo
                        document.getElementById('cash').checked = true;
                        document.getElementById('cash').dispatchEvent(new Event('change'));
                        return;
                    }
                }

                validatePayment();
            }
        });
    });

    // Selección de tipo de cliente
    document.querySelectorAll('.customer-type').forEach(type => {
        type.addEventListener('click', function () {
            document.querySelectorAll('.customer-type').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            this.querySelector('input[type="radio"]').checked = true;

            const customerType = this.querySelector('input').value;

            // Check if "Con datos" option is selected
            if (customerType === 'auto_data_customer') {
                // Show notification
                alert('Esta opción no está disponible actualmente.');

                // Deselect "Con datos" option and select "Consumidor Final" by default
                document.getElementById('final_consumer').checked = true;
                document.querySelectorAll('.customer-type').forEach(t => t.classList.remove('active'));
                document.getElementById('final_consumer').closest('.customer-type').classList.add('active');

                // Update customer type
                customerType = 'final_consumer';
            }

            if (registeredCustomerSection) {
                registeredCustomerSection.classList.toggle('hidden', customerType === 'final_consumer');

                // Re-enable invoice checkbox for registered customers
                if (invoiceRequiredCheckbox && customerType === 'registered_customer') {
                    invoiceRequiredCheckbox.disabled = false;
                    invoiceRequiredCheckbox.parentElement.classList.remove('opacity-50', 'cursor-not-allowed');

                    // Remove message if it exists
                    const messageElement = document.getElementById('invoice-disabled-message');
                    if (messageElement) {
                        messageElement.remove();
                    }
                }
            }
        });
    });

    // Funcionalidad del botón "Cambiar" cliente
    const changeCustomerBtn = document.getElementById('change-customer-btn');
    const customerSelectionModal = document.getElementById('customer-selection-modal');

    if (changeCustomerBtn && customerSelectionModal) {
        changeCustomerBtn.addEventListener('click', function () {
            customerSelectionModal.classList.toggle('hidden');
        });
    }

    // Lógica del panel numérico
    document.querySelectorAll('.num-pad-btn').forEach(button => {
        button.addEventListener('click', function () {
            const value = this.getAttribute('data-value');
            if (!cashAmountInput) return;

            let currentValue = cashAmountInput.value || '';

            if (value === 'clear') {
                cashAmountInput.value = '';
                if (cashChangeInput) cashChangeInput.value = '';
            } else if (value === '.') {
                if (!currentValue.includes('.')) {
                    cashAmountInput.value = currentValue + '.';
                }
            } else if (value === '00') {
                cashAmountInput.value = currentValue + '00';
            } else {
                cashAmountInput.value = currentValue + value;
            }
            calculateChange();
        });
    });

    // Lógica de montos rápidos
    document.querySelectorAll('.quick-amount-btn').forEach(button => {
        button.addEventListener('click', function () {
            if (!cashAmountInput) return;

            const value = this.getAttribute('data-value');
            if (value === 'exact') {
                // Obtener el total actual con descuento desde el DOM
                const cobrarAmountElement = document.getElementById('cobrar-amount');
                const currentTotal = cobrarAmountElement ?
                    parseFloat(cobrarAmountElement.textContent.replace('$', '').trim()) :
                    totalAmount;
                cashAmountInput.value = currentTotal.toFixed(2);
            } else {
                cashAmountInput.value = value;
            }
            calculateChange();
        });
    });

    // Entrada por teclado para efectivo
    if (cashAmountInput) {
        cashAmountInput.addEventListener('input', calculateChange);
    }

    // Formato y validación de tarjeta
    if (cardNumberInput) {
        cardNumberInput.addEventListener('input', function (e) {
            let value = e.target.value.replace(/\D/g, '').substring(0, 16);
            value = value.match(/.{1,4}/g)?.join(' ') || value;
            e.target.value = value;
            validatePayment();
        });
    }

    if (cardExpiryInput) {
        cardExpiryInput.addEventListener('input', function (e) {
            let value = e.target.value.replace(/\D/g, '').substring(0, 4);
            if (value.length >= 2) value = value.substring(0, 2) + '/' + value.substring(2);
            e.target.value = value;
            validatePayment();
        });
    }

    if (cardCvvInput) {
        cardCvvInput.addEventListener('input', function (e) {
            e.target.value = e.target.value.replace(/\D/g, '').substring(0, 4);
            validatePayment();
        });
    }

    if (cardNameInput) {
        cardNameInput.addEventListener('input', validatePayment);
    }

    // Cálculo del cambio en tiempo real con validación visual
    function calculateChange() {
        if (!cashAmountInput || !cashChangeInput) return;

        const cashAmount = parseFloat(cashAmountInput.value) || 0;

        // Obtener el total actual con descuento desde el DOM
        const cobrarAmountElement = document.getElementById('cobrar-amount');
        const currentTotal = cobrarAmountElement ?
            parseFloat(cobrarAmountElement.textContent.replace('$', '').trim()) :
            totalAmount;

        const change = cashAmount - currentTotal;
        const paymentValidation = document.getElementById('payment-validation');
        const validationMessage = document.getElementById('validation-message');
        const changeStatus = document.getElementById('change-status');

        if (cashAmount >= currentTotal) {
            cashChangeInput.value = '$' + change.toFixed(2);
            cashChangeInput.classList.remove('text-red-600', 'bg-red-50', 'border-red-400');
            cashChangeInput.classList.add('text-emerald-600', 'bg-white', 'border-emerald-400');

            // Ocultar mensaje de validación
            if (paymentValidation) {
                paymentValidation.classList.add('hidden');
                paymentValidation.classList.remove('bg-red-100', 'border-red-300', 'text-red-800');
            }

            // Mostrar estado del cambio
            if (changeStatus) {
                if (change === 0) {
                    changeStatus.innerHTML = '<i data-lucide="check" class="w-4 h-4 inline mr-1"></i> Pago exacto';
                    changeStatus.className = 'mt-3 text-center text-sm font-semibold text-emerald-600';
                } else {
                    changeStatus.innerHTML = '<i data-lucide="arrow-down-circle" class="w-4 h-4 inline mr-1"></i> Devolver cambio al cliente';
                    changeStatus.className = 'mt-3 text-center text-sm font-semibold text-blue-600';
                }
                changeStatus.classList.remove('hidden');
                // Re-initialize Lucide icons for dynamically added content
                if (typeof lucide !== 'undefined') {
                    lucide.createIcons();
                }
            }

            // Update hidden inputs for form submission
            const montoRecibidoInput = document.getElementById('monto_recibido');
            const cambioInput = document.getElementById('cambio');

            if (montoRecibidoInput) montoRecibidoInput.value = cashAmount.toFixed(2);
            if (cambioInput) cambioInput.value = change.toFixed(2);
        } else if (cashAmount > 0) {
            // Mostrar cuánto falta - MEJORA #5
            const falta = currentTotal - cashAmount;
            cashChangeInput.value = 'FALTA $' + falta.toFixed(2);
            cashChangeInput.classList.remove('text-emerald-600', 'bg-white', 'border-emerald-400');
            cashChangeInput.classList.add('text-red-600', 'bg-red-50', 'border-red-400');

            // Mostrar mensaje de validación en rojo
            if (paymentValidation && validationMessage) {
                paymentValidation.classList.remove('hidden', 'bg-emerald-100', 'border-emerald-300', 'text-emerald-800');
                paymentValidation.classList.add('bg-red-100', 'border-2', 'border-red-300', 'text-red-800');
                validationMessage.innerHTML = `<i data-lucide="alert-triangle" class="w-5 h-5 inline mr-2"></i> FALTA $${falta.toFixed(2)}`;
                // Re-initialize Lucide icons
                if (typeof lucide !== 'undefined') {
                    lucide.createIcons();
                }
            }

            // Ocultar estado del cambio
            if (changeStatus) {
                changeStatus.classList.add('hidden');
            }

            // Clear hidden inputs if amount is insufficient
            const montoRecibidoInput = document.getElementById('monto_recibido');
            const cambioInput = document.getElementById('cambio');

            if (montoRecibidoInput) montoRecibidoInput.value = '0';
            if (cambioInput) cambioInput.value = '0';
        } else {
            cashChangeInput.value = '';
            cashChangeInput.classList.remove('text-red-600', 'bg-red-50', 'border-red-400', 'text-emerald-600', 'bg-white', 'border-emerald-400');

            if (paymentValidation) {
                paymentValidation.classList.add('hidden');
            }

            if (changeStatus) {
                changeStatus.classList.add('hidden');
            }
        }
        validatePayment();
    }

    // Validación para habilitar el botón de procesar pago
    function validatePayment() {
        if (!processPaymentBtn || !metodoPagoInput) return;

        const metodoPago = metodoPagoInput.value;
        let isValid = false;

        console.log('🔍 validatePayment() ejecutándose');
        console.log('   - Método de pago:', metodoPago);

        if (metodoPago === 'cash') {
            const cashAmount = parseFloat(cashAmountInput?.value) || 0;
            // Obtener el total actual con descuento desde el DOM
            const cobrarAmountElement = document.getElementById('cobrar-amount');
            const currentTotal = cobrarAmountElement ?
                parseFloat(cobrarAmountElement.textContent.replace('$', '').trim()) :
                totalAmount;
            isValid = cashAmount >= currentTotal;
            console.log('   - Efectivo: monto=', cashAmount, 'total=', currentTotal, 'válido=', isValid);
        } else if (metodoPago === 'card') {
            const cardNumberValid = cardNumberInput?.value.replace(/\s/g, '').length === 16;
            const cardNameValid = cardNameInput?.value.trim().length > 0;
            const cardExpiryValid = cardExpiryInput?.value.match(/^\d{2}\/\d{2}$/);
            const cardCvvValid = cardCvvInput?.value.length >= 3;
            isValid = cardNumberValid && cardNameValid && cardExpiryValid && cardCvvValid;
            console.log('   - Tarjeta: válido=', isValid);
        } else if (metodoPago === 'transfer') {
            isValid = true;
            console.log('   - Transferencia: siempre válido');
        } else if (metodoPago === 'credit') {
            // Crédito: verificar si el botón está en amarillo (sin cupo)
            const creditOption = document.getElementById('credit-payment-option');
            const hasWarning = creditOption && creditOption.classList.contains('bg-yellow-50');
            isValid = !hasWarning; // Solo válido si NO está en amarillo (tiene cupo)
            console.log('   - Crédito: tiene advertencia=', hasWarning, 'válido=', isValid);
            console.log('   - Clases del botón crédito:', creditOption?.className);
        }

        console.log('   ➡️ Resultado final: isValid=', isValid);
        console.log('   ➡️ Deshabilitando botón:', !isValid);
        processPaymentBtn.disabled = !isValid;
    }

    // Inicializar la validación al cargar la página
    validatePayment();

    // Deshabilitar crédito si es consumidor final al cargar
    const clienteIdInput = document.getElementById('cliente_id_input');
    const creditOption = document.getElementById('credit-payment-option');
    const creditRadio = document.getElementById('credit');
    const creditIconBtn = document.getElementById('credit-icon-btn');
    const creditInfo = document.getElementById('credit-info');

    if (creditOption && creditRadio) {
        if (!clienteIdInput || !clienteIdInput.value) {
            // No hay cliente seleccionado (Consumidor Final)
            creditOption.classList.add('opacity-50', 'cursor-not-allowed', 'bg-gray-50', 'border-gray-200');
            creditRadio.disabled = true;

            if (creditIconBtn) {
                creditIconBtn.classList.add('text-gray-400');
            }

            if (creditInfo) {
                creditInfo.textContent = 'Seleccione un cliente para habilitar crédito';
                creditInfo.classList.add('text-gray-500');
            }
        } else {
            // Hay un cliente seleccionado, verificar su estado de crédito
            const aplicarClienteDescuentosUrl = window.DJANGO_VARS?.aplicarClienteDescuentosUrl;
            if (aplicarClienteDescuentosUrl) {
                fetch(aplicarClienteDescuentosUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        venta_id: window.DJANGO_VARS?.ventaId,
                        cliente_id: clienteIdInput.value
                    })
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success && data.cliente) {
                            const creditWarning = document.getElementById('credit-warning');
                            const creditIcon = document.getElementById('credit-icon');
                            const creditTitle = document.getElementById('credit-title');

                            if (data.cliente.puede_credito) {
                                // Cliente CON crédito - Verde y habilitado
                                creditOption.classList.remove('opacity-50', 'cursor-not-allowed', 'bg-gray-50', 'border-gray-200', 'bg-yellow-50', 'border-yellow-300');
                                creditOption.classList.add('bg-emerald-50', 'border-emerald-300', 'hover:border-emerald-500', 'hover:bg-emerald-100');
                                creditRadio.disabled = false;

                                if (creditIconBtn) {
                                    creditIconBtn.classList.remove('text-gray-400', 'text-yellow-600');
                                    creditIconBtn.classList.add('text-emerald-600');
                                }

                                if (creditInfo) {
                                    creditInfo.textContent = `Disponible: ${data.cliente.credito_dias} días, Cupo: $${data.cliente.cupo.toFixed(2)}`;
                                    creditInfo.classList.remove('text-gray-500', 'text-yellow-700');
                                    creditInfo.classList.add('text-emerald-700', 'font-semibold');
                                }

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
                            } else {
                                // Cliente SIN crédito suficiente - Amarillo con advertencia
                                creditOption.classList.remove('opacity-50', 'cursor-not-allowed', 'bg-gray-50', 'border-gray-200');
                                creditOption.classList.add('bg-yellow-50', 'border-yellow-300', 'hover:border-yellow-500', 'hover:bg-yellow-100');
                                creditRadio.disabled = false;

                                if (creditIconBtn) {
                                    creditIconBtn.classList.remove('text-gray-400', 'text-emerald-600');
                                    creditIconBtn.classList.add('text-yellow-600');
                                }

                                if (creditInfo) {
                                    let mensaje = '';
                                    if (data.cliente.credito_dias <= 0) {
                                        mensaje = 'Cliente sin crédito habilitado';
                                    } else if (data.cliente.cupo <= 0) {
                                        mensaje = 'Sin cupo disponible (Cupo: $0.00)';
                                    } else {
                                        mensaje = `Cupo insuficiente (Disponible: $${data.cliente.cupo.toFixed(2)})`;
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
                            }

                            // Re-initialize Lucide icons
                            if (typeof lucide !== 'undefined') {
                                lucide.createIcons();
                            }
                        }
                    })
                    .catch(error => {
                        console.error('Error al verificar estado de crédito:', error);
                    });
            }
        }
    }

    // Atajos de teclado - MEJORA #4
    document.addEventListener('keydown', function (e) {
        // ENTER → cobrar (solo si el botón está habilitado)
        if (e.key === 'Enter' && !processPaymentBtn.disabled && !e.target.matches('input, textarea')) {
            e.preventDefault();
            processPaymentBtn.click();
        }

        // ESC → cancelar
        if (e.key === 'Escape') {
            e.preventDefault();
            if (confirm('¿Desea cancelar y volver a ventas?')) {
                window.location.href = document.querySelector('a[href*="ventas"]').href;
            }
        }

        // F2 → seleccionar efectivo
        if (e.key === 'F2') {
            e.preventDefault();
            const cashRadio = document.getElementById('cash');
            if (cashRadio) {
                cashRadio.checked = true;
                cashRadio.dispatchEvent(new Event('change'));
            }
        }

        // F3 → seleccionar tarjeta
        if (e.key === 'F3') {
            e.preventDefault();
            const cardRadio = document.getElementById('card');
            if (cardRadio) {
                cardRadio.checked = true;
                cardRadio.dispatchEvent(new Event('change'));
            }
        }
    });

    // Client selection functionality
    const finalConsumerRadio = document.getElementById('final_consumer');
    const registeredCustomerRadio = document.getElementById('registered_customer');
    const clientSelection = document.getElementById('client-selection');
    const clientSearch = document.getElementById('client-search');
    const clientResults = document.getElementById('client-results');
    const clientResultsBody = document.getElementById('client-results-body');
    const selectedClientInfo = document.getElementById('selected-client-info');
    const selectedClientName = document.getElementById('selected-client-name');
    const selectedClientId = document.getElementById('selected-client-id');
    const selectedClientAddress = document.getElementById('selected-client-address');
    const selectedClientIdInput = document.getElementById('selected-client-id-input');
    const changeClientBtn = document.getElementById('change-client');

    // Toggle client selection based on customer type
    if (finalConsumerRadio) {
        finalConsumerRadio.addEventListener('change', function () {
            if (this.checked && clientSelection) {
                clientSelection.classList.add('hidden');
                // Reset selected client
                if (selectedClientIdInput) selectedClientIdInput.value = '';
            }
        });
    }

    if (registeredCustomerRadio) {
        registeredCustomerRadio.addEventListener('change', function () {
            if (this.checked && clientSelection) {
                clientSelection.classList.remove('hidden');
            }
        });
    }

    // Client search functionality
    let searchTimeout;
    if (clientSearch) {
        clientSearch.addEventListener('input', function () {
            const searchTerm = this.value.trim();

            // Clear previous timeout
            clearTimeout(searchTimeout);

            if (searchTerm.length < 2) {
                if (clientResults) clientResults.classList.add('hidden');
                return;
            }

            // Set a timeout to avoid too many requests
            searchTimeout = setTimeout(() => {
                // The server-side search will now look for matches in both name and identification
                fetch(`/clients/search/?q=${encodeURIComponent(searchTerm)}`, {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'Accept': 'application/json',
                    }
                })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.json();
                    })
                    .then(data => {
                        if (!clientResultsBody) return;

                        clientResultsBody.innerHTML = '';

                        // Changed from data.results to data
                        if (!data || data.length === 0) {
                            clientResultsBody.innerHTML = `
                                <tr>
                                    <td colspan="4" class="px-4 py-3 text-center text-gray-500">
                                        No se encontraron clientes
                                    </td>
                                </tr>
                            `;
                        } else {
                            // Changed from data.results.forEach to data.forEach
                            data.forEach(client => {
                                const row = document.createElement('tr');
                                row.className = 'hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer';
                                row.innerHTML = `
                                    <td class="px-4 py-2 text-sm">${client.codigo || '-'}</td>
                                    <td class="px-4 py-2 text-sm">${client.nombre}</td>
                                    <td class="px-4 py-2 text-sm">${client.identificacion}</td>
                                    <td class="px-4 py-2 text-sm">
                                        <button class="select-client-btn bg-emerald-100 hover:bg-emerald-200 text-emerald-800 px-2 py-1 rounded text-xs"
                                                data-client-id="${client.id}"
                                                data-client-name="${client.nombre}"
                                                data-client-identification="${client.identificacion}"
                                                data-client-address="${client.direccion || ''}"
                                                data-client-city="${client.ciudad || ''}">
                                            Seleccionar
                                        </button>
                                    </td>
                                `;
                                clientResultsBody.appendChild(row);
                            });
                        }

                        if (clientResults) clientResults.classList.remove('hidden');

                        // Add event listeners to select client buttons
                        document.querySelectorAll('.select-client-btn').forEach(btn => {
                            btn.addEventListener('click', function () {
                                const clientId = this.dataset.clientId;
                                const clientName = this.dataset.clientName;
                                const clientIdentification = this.dataset.clientIdentification;
                                const clientAddress = this.dataset.clientAddress;
                                const clientCity = this.dataset.clientCity;

                                // Update selected client info
                                if (selectedClientName) selectedClientName.textContent = clientName;
                                if (selectedClientId) selectedClientId.textContent = `Cédula/RUC: ${clientIdentification}`;

                                let addressText = '';
                                if (clientAddress) {
                                    addressText += clientAddress;
                                }
                                if (clientCity) {
                                    if (addressText) addressText += ', ';
                                    addressText += clientCity;
                                }
                                if (selectedClientAddress) selectedClientAddress.textContent = addressText || 'Sin dirección';

                                // Update hidden input
                                if (selectedClientIdInput) selectedClientIdInput.value = clientId;

                                // 🎯 Actualizar también el input del formulario de pago
                                const clienteIdInput = document.getElementById('cliente_id_input');
                                if (clienteIdInput) clienteIdInput.value = clientId;

                                // Show selected client info and hide search results
                                if (selectedClientInfo) selectedClientInfo.classList.remove('hidden');
                                if (clientResults) clientResults.classList.add('hidden');
                                if (clientSearch) clientSearch.value = '';

                                // 🎯 Llamar a la API para aplicar descuentos/recargos del cliente
                                const aplicarClienteDescuentosUrl = window.DJANGO_VARS?.aplicarClienteDescuentosUrl;
                                console.log('=== APLICAR DESCUENTOS ===');
                                console.log('URL:', aplicarClienteDescuentosUrl);
                                console.log('Venta ID:', window.DJANGO_VARS?.ventaId);
                                console.log('Cliente ID:', clientId);

                                if (aplicarClienteDescuentosUrl) {
                                    fetch(aplicarClienteDescuentosUrl, {
                                        method: 'POST',
                                        headers: {
                                            'Content-Type': 'application/json',
                                            'X-CSRFToken': getCookie('csrftoken')
                                        },
                                        body: JSON.stringify({
                                            venta_id: window.DJANGO_VARS?.ventaId,
                                            cliente_id: clientId
                                        })
                                    })
                                        .then(response => response.json())
                                        .then(data => {
                                            if (data.success) {
                                                // Actualizar información del cliente
                                                const clientDetails = document.getElementById('client-details');
                                                if (clientDetails && !data.cliente.es_consumidor_final) {
                                                    clientDetails.classList.remove('hidden');

                                                    document.getElementById('client-grupo').textContent = data.cliente.grupo;
                                                    document.getElementById('client-estado').textContent = data.cliente.estado;
                                                    document.getElementById('client-credito').textContent = data.cliente.credito_dias + ' días';
                                                    document.getElementById('client-cupo').textContent = '$' + data.cliente.cupo.toFixed(2);
                                                    document.getElementById('client-descuento').textContent = data.cliente.tasa_descuento.toFixed(2) + '%';
                                                    document.getElementById('client-recargo').textContent = data.cliente.tasa_recargo.toFixed(2) + '%';
                                                }

                                                // Actualizar totales
                                                document.getElementById('display-subtotal').textContent = '$' + data.totales.subtotal.toFixed(2);
                                                document.getElementById('display-iva').textContent = '$' + data.totales.iva.toFixed(2);
                                                document.getElementById('display-total').textContent = '$' + data.totales.total.toFixed(2);

                                                // Actualizar botón COBRAR
                                                const cobrarAmount = document.getElementById('cobrar-amount');
                                                if (cobrarAmount) cobrarAmount.textContent = '$' + data.totales.total.toFixed(2);

                                                // Actualizar variable totalAmount
                                                totalAmount = data.totales.total;
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

                                                // Volver al método de pago Efectivo
                                                const cashRadio = document.getElementById('cash');
                                                console.log('🔄 Cambiando a método de pago Efectivo');
                                                if (cashRadio) {
                                                    cashRadio.checked = true;
                                                    // Actualizar el input oculto del método de pago
                                                    const metodoPagoInput = document.getElementById('metodo_pago_input');
                                                    if (metodoPagoInput) metodoPagoInput.value = 'cash';

                                                    // Actualizar las clases visuales
                                                    document.querySelectorAll('.payment-method').forEach(m => m.classList.remove('active'));
                                                    cashRadio.closest('.payment-method').classList.add('active');

                                                    // Mostrar/ocultar secciones de pago
                                                    const cashPaymentDetails = document.getElementById('cash-payment-details');
                                                    const cardPaymentDetails = document.getElementById('card-payment-details');
                                                    const creditWarning = document.getElementById('credit-warning');

                                                    if (cashPaymentDetails) cashPaymentDetails.classList.remove('hidden');
                                                    if (cardPaymentDetails) cardPaymentDetails.classList.add('hidden');
                                                    if (creditWarning) creditWarning.classList.add('hidden');
                                                }

                                                // Deshabilitar botón COBRAR hasta que se ingrese un monto
                                                const processPaymentBtn = document.getElementById('process-payment');
                                                console.log('🔒 Deshabilitando botón COBRAR');
                                                if (processPaymentBtn) {
                                                    processPaymentBtn.disabled = true;
                                                }

                                                // Mostrar/ocultar descuento
                                                const descuentoRow = document.getElementById('descuento-row');
                                                if (data.totales.descuento_total > 0) {
                                                    descuentoRow.classList.remove('hidden');
                                                    const porcentaje = data.cliente && data.cliente.tasa_descuento ? ` (${data.cliente.tasa_descuento.toFixed(1)}%)` : '';
                                                    document.getElementById('display-descuento').textContent = '-$' + data.totales.descuento_total.toFixed(2) + porcentaje;
                                                } else {
                                                    descuentoRow.classList.add('hidden');
                                                }

                                                // Mostrar/ocultar recargo
                                                const recargoRow = document.getElementById('recargo-row');
                                                if (data.totales.recargo_total > 0) {
                                                    recargoRow.classList.remove('hidden');
                                                    const porcentaje = data.cliente && data.cliente.tasa_recargo ? ` (${data.cliente.tasa_recargo.toFixed(1)}%)` : '';
                                                    document.getElementById('display-recargo').textContent = '+$' + data.totales.recargo_total.toFixed(2) + porcentaje;
                                                } else {
                                                    recargoRow.classList.add('hidden');
                                                }

                                                // Habilitar/deshabilitar opción de crédito
                                                const creditOption = document.getElementById('credit-payment-option');
                                                const creditRadio = document.getElementById('credit');
                                                const creditWarning = document.getElementById('credit-warning');
                                                const creditInfo = document.getElementById('credit-info');
                                                const creditIcon = document.getElementById('credit-icon');
                                                const creditIconBtn = document.getElementById('credit-icon-btn');
                                                const creditTitle = document.getElementById('credit-title');

                                                console.log('💳 Evaluando estado de crédito del cliente');
                                                console.log('   - Cliente:', data.cliente.nombre);
                                                console.log('   - puede_credito:', data.cliente.puede_credito);
                                                console.log('   - cupo:', data.cliente.cupo);
                                                console.log('   - total:', data.totales.total);

                                                if (data.cliente.puede_credito) {
                                                    // Cliente CON crédito - Verde y habilitado
                                                    creditOption.classList.remove('opacity-50', 'cursor-not-allowed', 'bg-gray-50', 'border-gray-200');
                                                    creditOption.classList.add('bg-emerald-50', 'border-emerald-300', 'hover:border-emerald-500', 'hover:bg-emerald-100');
                                                    creditRadio.disabled = false;

                                                    if (creditIconBtn) {
                                                        creditIconBtn.classList.remove('text-gray-400', 'text-yellow-600');
                                                        creditIconBtn.classList.add('text-emerald-600');
                                                    }

                                                    if (creditInfo) {
                                                        creditInfo.textContent = `Disponible: ${data.cliente.credito_dias} días, Cupo: $${data.cliente.cupo.toFixed(2)}`;
                                                        creditInfo.classList.remove('text-gray-500', 'text-yellow-700');
                                                        creditInfo.classList.add('text-emerald-700', 'font-semibold');
                                                    }

                                                    // Actualizar el warning box cuando se seleccione crédito
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
                                                } else {
                                                    // Cliente SIN crédito suficiente - OCULTAR el botón
                                                    console.log('🚫 Cliente SIN crédito suficiente');
                                                    console.log('   - puede_credito:', data.cliente.puede_credito);
                                                    console.log('   - cupo:', data.cliente.cupo);
                                                    console.log('   - credito_dias:', data.cliente.credito_dias);
                                                    console.log('   - total venta:', data.totales.total);
                                                    console.log('   - creditOption element:', creditOption);
                                                    
                                                    if (creditOption) {
                                                        console.log('   ✅ Agregando clase hidden al botón de crédito');
                                                        creditOption.classList.add('hidden');
                                                        console.log('   - Clases después:', creditOption.className);
                                                    } else {
                                                        console.log('   ❌ No se encontró el elemento creditOption');
                                                    }
                                                    
                                                    creditRadio.disabled = true;

                                                    // Si estaba seleccionado crédito, cambiar a efectivo
                                                    if (creditRadio.checked) {
                                                        console.log('   🔄 Crédito estaba seleccionado, cambiando a efectivo');
                                                        const cashRadio = document.getElementById('cash');
                                                        if (cashRadio) {
                                                            cashRadio.checked = true;
                                                            const metodoPagoInput = document.getElementById('metodo_pago_input');
                                                            if (metodoPagoInput) metodoPagoInput.value = 'cash';

                                                            document.querySelectorAll('.payment-method').forEach(m => m.classList.remove('active'));
                                                            cashRadio.closest('.payment-method').classList.add('active');

                                                            const cashPaymentDetails = document.getElementById('cash-payment-details');
                                                            const cardPaymentDetails = document.getElementById('card-payment-details');
                                                            if (cashPaymentDetails) cashPaymentDetails.classList.remove('hidden');
                                                            if (cardPaymentDetails) cardPaymentDetails.classList.add('hidden');
                                                        }
                                                    }

                                                    // Ocultar el warning
                                                    if (creditWarning) {
                                                        creditWarning.classList.add('hidden');
                                                    }
                                                }

                                                // Re-initialize Lucide icons
                                                if (typeof lucide !== 'undefined') {
                                                    lucide.createIcons();
                                                }

                                                // Actualizar el total global para cálculos
                                                window.DJANGO_VARS.total = data.totales.total;
                                            }
                                        })
                                        .catch(error => {
                                            console.error('Error al aplicar descuentos:', error);
                                        });
                                }

                                // Update the sale with the selected client
                                // Ya no es necesario porque aplicar-cliente-descuentos hace todo
                                /*
                                const csrftoken = getCookie('csrftoken');

                                fetch(actualizarClienteUrl, {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/x-www-form-urlencoded',
                                        'X-CSRFToken': csrftoken
                                    },
                                    body: new URLSearchParams({
                                        'client_id': clientId
                                    })
                                })
                                    .then(response => response.json())
                                    .then(data => {
                                        if (!data.success) {
                                            console.error('Error al actualizar cliente:', data.error);
                                        }
                                    })
                                    .catch(error => {
                                        console.error('Error:', error);
                                    });
                                */
                            });
                        });
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        if (clientResultsBody) {
                            clientResultsBody.innerHTML = `
                                <tr>
                                    <td colspan="4" class="px-4 py-3 text-center text-red-500">
                                        Error al buscar clientes: ${error.message}
                                    </td>
                                </tr>
                            `;
                        }
                        if (clientResults) clientResults.classList.remove('hidden');
                    });
            }, 300);
        });
    }

    // Change client button
    if (changeClientBtn) {
        changeClientBtn.addEventListener('click', function () {
            if (selectedClientInfo) selectedClientInfo.classList.add('hidden');
            if (clientSearch) clientSearch.value = '';
            if (clientResults) clientResults.classList.add('hidden');
            if (selectedClientIdInput) selectedClientIdInput.value = '';
        });
    }
});