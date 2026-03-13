/* ============================================
   LEMON POS - REGISTER PAGE JAVASCRIPT
   ============================================ */

document.addEventListener('DOMContentLoaded', function() {
    
    let currentStep = 1;
    const totalSteps = 5; // 5 pasos: Cuenta, Negocio, Fiscal, Plan, Listo
    let emailAvailable = true; // Variable para rastrear disponibilidad del email

    const nextBtn = document.getElementById('nextBtn');
    const prevBtn = document.getElementById('prevBtn');
    const submitBtn = document.getElementById('submitBtn');
    const progressBar = document.getElementById('progressBar');

    // Toast notifications
    function showToast(message, type = 'error') {
        const container = document.getElementById('toast-container') || createToastContainer();
        const toast = document.createElement('div');
        const iconColor = type === 'error' ? '#ef4444' : '#22c55e';
        const icon = type === 'error' ? 'M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z' : 'M5 13l4 4L19 7';
        
        toast.className = 'toast';
        toast.innerHTML = `
            <svg class="toast-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: ${iconColor};">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${icon}"></path>
            </svg>
            <div class="toast-content">
                <div class="toast-title">${type === 'error' ? 'Error de validación' : 'Éxito'}</div>
                <div class="toast-message">${message}</div>
            </div>
        `;

        container.appendChild(toast);
        setTimeout(() => toast.classList.add('show'), 10);
        setTimeout(() => {
            toast.classList.add('hide');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    function createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = 'position: fixed; top: 80px; right: 20px; z-index: 9999;';
        document.body.appendChild(container);
        return container;
    }

    // Función para seleccionar plan
    window.selectPlan = function(plan, element) {
        if (element.classList.contains('disabled')) return;

        document.querySelectorAll('.plan-card').forEach(card => {
            card.classList.remove('selected');
            card.style.borderColor = '#e5e7eb';
            const badge = card.querySelector('.text-center > span:last-child');
            if (badge && badge.textContent === 'Seleccionado') {
                badge.remove();
            }
        });

        element.classList.add('selected');
        element.style.borderColor = 'var(--color-primary)';
        
        const badge = document.createElement('span');
        badge.className = 'inline-block px-4 py-2 rounded-lg text-sm font-medium';
        badge.style.backgroundColor = 'rgba(34, 197, 94, 0.1)';
        badge.style.color = 'var(--color-primary)';
        badge.textContent = 'Seleccionado';
        element.querySelector('.text-center').appendChild(badge);

        document.getElementById('selectedPlan').value = plan;
    };

    // Validation
    function validateStep(step) {
        let isValid = true;
        let errorMessage = '';
        let errorField = null;

        if (step === 1) {
            const nombreInput = document.querySelector('input[name="nombre_completo"]');
            const emailInput = document.querySelector('input[name="email"]');
            const password1Input = document.querySelector('input[name="password1"]');
            const password2Input = document.querySelector('input[name="password2"]');
            
            const nombre = nombreInput.value.trim();
            const email = emailInput.value.trim();
            const password1 = password1Input.value;
            const password2 = password2Input.value;

            if (!nombre) {
                errorMessage = 'Por favor ingresa tu nombre completo';
                errorField = nombreInput;
                isValid = false;
            } else if (!email) {
                errorMessage = 'Por favor ingresa tu email';
                errorField = emailInput;
                isValid = false;
            } else if (!email.includes('@') || !email.includes('.')) {
                errorMessage = 'Por favor ingresa un email válido';
                errorField = emailInput;
                isValid = false;
            } else if (!emailAvailable) {
                errorMessage = 'Este email ya está registrado. Por favor usa otro email.';
                errorField = emailInput;
                isValid = false;
            } else if (!password1 || password1.length < 8) {
                errorMessage = 'La contraseña debe tener al menos 8 caracteres';
                errorField = password1Input;
                isValid = false;
            } else if (!/[a-z]/.test(password1)) {
                errorMessage = 'La contraseña debe contener al menos una letra minúscula';
                errorField = password1Input;
                isValid = false;
            } else if (!/[A-Z]/.test(password1)) {
                errorMessage = 'La contraseña debe contener al menos una letra mayúscula';
                errorField = password1Input;
                isValid = false;
            } else if (!/[0-9]/.test(password1)) {
                errorMessage = 'La contraseña debe contener al menos un número';
                errorField = password1Input;
                isValid = false;
            } else if (password1 !== password2) {
                errorMessage = 'Las contraseñas no coinciden';
                errorField = password2Input;
                isValid = false;
            }
        } else if (step === 2) {
            const nombreNegocioInput = document.querySelector('input[name="nombre_negocio"]');
            const emailNegocioInput = document.querySelector('input[name="email_negocio"]');
            const rucInput = document.querySelector('input[name="ruc_negocio"]');
            
            const nombreNegocio = nombreNegocioInput.value.trim();
            const emailNegocio = emailNegocioInput.value.trim();
            const ruc = rucInput.value.trim();

            if (!nombreNegocio) {
                errorMessage = 'Por favor ingresa el nombre del negocio';
                errorField = nombreNegocioInput;
                isValid = false;
            } else if (emailNegocio && (!emailNegocio.includes('@') || !emailNegocio.includes('.'))) {
                errorMessage = 'El email del negocio no es válido';
                errorField = emailNegocioInput;
                isValid = false;
            } else if (ruc && ruc.length > 0 && ruc.length !== 13) {
                errorMessage = 'El RUC debe tener exactamente 13 dígitos';
                errorField = rucInput;
                isValid = false;
            } else if (ruc && !/^\d+$/.test(ruc)) {
                errorMessage = 'El RUC solo debe contener números';
                errorField = rucInput;
                isValid = false;
            }
        } else if (step === 3) {
            const establecimientoInput = document.querySelector('input[name="establecimiento"]');
            const puntoEmisionInput = document.querySelector('input[name="punto_emision"]');
            
            const establecimiento = establecimientoInput.value.trim();
            const puntoEmision = puntoEmisionInput.value.trim();

            if (establecimiento && establecimiento.length > 0 && establecimiento.length !== 3) {
                errorMessage = 'El establecimiento debe tener exactamente 3 dígitos';
                errorField = establecimientoInput;
                isValid = false;
            } else if (establecimiento && !/^\d+$/.test(establecimiento)) {
                errorMessage = 'El establecimiento solo debe contener números';
                errorField = establecimientoInput;
                isValid = false;
            } else if (puntoEmision && puntoEmision.length > 0 && puntoEmision.length !== 3) {
                errorMessage = 'El punto de emisión debe tener exactamente 3 dígitos';
                errorField = puntoEmisionInput;
                isValid = false;
            } else if (puntoEmision && !/^\d+$/.test(puntoEmision)) {
                errorMessage = 'El punto de emisión solo debe contener números';
                errorField = puntoEmisionInput;
                isValid = false;
            }
        }

        if (!isValid) {
            showToast(errorMessage);
            if (errorField) {
                errorField.classList.add('field-error');
                errorField.focus();
                errorField.addEventListener('input', function() {
                    this.classList.remove('field-error');
                }, { once: true });
            }
        }

        return isValid;
    }

    // Show step
    function showStep(step) {
        document.querySelectorAll('.step-content').forEach(content => {
            content.classList.remove('active', 'prev');
            if (parseInt(content.dataset.step) < step) {
                content.classList.add('prev');
            }
        });

        const currentContent = document.querySelector(`.step-content[data-step="${step}"]`);
        if (currentContent) {
            setTimeout(() => currentContent.classList.add('active'), 50);
        }

        // Actualizar indicadores de paso
        document.querySelectorAll('.step-indicator').forEach(indicator => {
            const indicatorStep = parseInt(indicator.dataset.step);
            const circle = indicator.querySelector('div');
            const text = indicator.querySelector('p');
            
            if (indicatorStep <= step) {
                circle.classList.remove('bg-gray-200', 'text-gray-400');
                circle.classList.add('text-white');
                circle.style.backgroundColor = 'var(--color-primary)';
                text.classList.remove('text-gray-400');
                text.style.color = 'var(--color-primary)';
            } else {
                circle.classList.remove('text-white');
                circle.classList.add('bg-gray-200', 'text-gray-400');
                circle.style.backgroundColor = '';
                text.classList.add('text-gray-400');
                text.style.color = '';
            }
        });

        const progress = (step / totalSteps) * 100;
        progressBar.style.width = progress + '%';

        // Update buttons
        prevBtn.style.display = step === 1 ? 'none' : 'flex';
        nextBtn.style.display = step === totalSteps ? 'none' : 'flex';
        submitBtn.style.display = step === totalSteps ? 'flex' : 'none';

        // Ocultar el link de "¿Ya tienes cuenta?" en el paso final
        const loginLink = document.getElementById('loginLink');
        if (loginLink) {
            loginLink.style.display = step === totalSteps ? 'none' : 'block';
        }

        currentStep = step;
    }

    // Navigation
    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            if (currentStep < totalSteps) {
                // Si es el paso 1, verificar email antes de validar
                if (currentStep === 1) {
                    const emailInput = document.querySelector('input[name="email"]');
                    const email = emailInput.value.trim();
                    
                    if (email && email.includes('@') && email.includes('.')) {
                        // Deshabilitar botón mientras verifica
                        nextBtn.disabled = true;
                        nextBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>Verificando...</span>';
                        
                        // Verificar email en el servidor
                        fetch('/accounts/check-email/', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/x-www-form-urlencoded',
                                'X-CSRFToken': getCookie('csrftoken')
                            },
                            body: 'email=' + encodeURIComponent(email)
                        })
                        .then(response => response.json())
                        .then(data => {
                            // Restaurar botón
                            nextBtn.disabled = false;
                            nextBtn.innerHTML = '<span>Siguiente</span><i class="fas fa-arrow-right"></i>';
                            
                            if (data.exists) {
                                emailAvailable = false;
                                emailInput.classList.add('field-error');
                                showToast('Este email ya está registrado. Por favor usa otro email.');
                            } else {
                                emailAvailable = true;
                                emailInput.classList.remove('field-error');
                                // Ahora sí validar y avanzar
                                if (validateStep(currentStep)) {
                                    showStep(currentStep + 1);
                                }
                            }
                        })
                        .catch(error => {
                            console.error('Error checking email:', error);
                            nextBtn.disabled = false;
                            nextBtn.innerHTML = '<span>Siguiente</span><i class="fas fa-arrow-right"></i>';
                            showToast('Error al verificar el email. Por favor intenta de nuevo.');
                        });
                    } else {
                        // Si el email no es válido, solo validar normalmente
                        if (validateStep(currentStep)) {
                            showStep(currentStep + 1);
                        }
                    }
                } else {
                    // Para otros pasos, validar normalmente
                    if (validateStep(currentStep)) {
                        showStep(currentStep + 1);
                    }
                }
            }
        });
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            if (currentStep > 1) {
                showStep(currentStep - 1);
            }
        });
    }

    // Password strength
    const password1Input = document.getElementById('password1');
    const passwordStrengthDiv = document.getElementById('password-strength');
    const strengthText = document.getElementById('password-strength-text');
    const strengthBars = [
        document.getElementById('strength-bar-1'),
        document.getElementById('strength-bar-2'),
        document.getElementById('strength-bar-3'),
        document.getElementById('strength-bar-4')
    ];
    const reqLength = document.getElementById('req-length');
    const reqLowercase = document.getElementById('req-lowercase');
    const reqUppercase = document.getElementById('req-uppercase');
    const reqNumber = document.getElementById('req-number');

    if (password1Input && passwordStrengthDiv) {
        password1Input.addEventListener('input', function() {
            const password = this.value;
            
            if (password.length > 0) {
                passwordStrengthDiv.classList.remove('hidden');

                // Verificar requisitos
                const hasLength = password.length >= 8;
                const hasLowercase = /[a-z]/.test(password);
                const hasUppercase = /[A-Z]/.test(password);
                const hasNumber = /[0-9]/.test(password);

                // Actualizar indicadores de requisitos
                if (reqLength) {
                    reqLength.textContent = hasLength ? '✓ Mínimo 8 caracteres' : '✗ Mínimo 8 caracteres';
                    reqLength.className = hasLength ? 'text-green-600' : 'text-gray-500';
                }
                if (reqLowercase) {
                    reqLowercase.textContent = hasLowercase ? '✓ Una letra minúscula' : '✗ Una letra minúscula';
                    reqLowercase.className = hasLowercase ? 'text-green-600' : 'text-gray-500';
                }
                if (reqUppercase) {
                    reqUppercase.textContent = hasUppercase ? '✓ Una letra mayúscula' : '✗ Una letra mayúscula';
                    reqUppercase.className = hasUppercase ? 'text-green-600' : 'text-gray-500';
                }
                if (reqNumber) {
                    reqNumber.textContent = hasNumber ? '✓ Un número' : '✗ Un número';
                    reqNumber.className = hasNumber ? 'text-green-600' : 'text-gray-500';
                }

                // Calcular fortaleza
                let strength = 0;
                if (hasLength) strength++;
                if (hasLowercase) strength++;
                if (hasUppercase) strength++;
                if (hasNumber) strength++;

                // Actualizar barras de fortaleza
                strengthBars.forEach((bar, index) => {
                    if (bar) {
                        if (index < strength) {
                            if (strength === 1) bar.style.backgroundColor = '#ef4444'; // Rojo
                            else if (strength === 2) bar.style.backgroundColor = '#f59e0b'; // Naranja
                            else if (strength === 3) bar.style.backgroundColor = '#eab308'; // Amarillo
                            else bar.style.backgroundColor = '#22c55e'; // Verde
                        } else {
                            bar.style.backgroundColor = '#e5e7eb'; // Gris
                        }
                    }
                });

                // Actualizar texto de fortaleza
                if (strengthText) {
                    if (strength === 1) {
                        strengthText.textContent = 'Contraseña débil';
                        strengthText.className = 'text-xs text-red-600';
                    } else if (strength === 2) {
                        strengthText.textContent = 'Contraseña regular';
                        strengthText.className = 'text-xs text-orange-600';
                    } else if (strength === 3) {
                        strengthText.textContent = 'Contraseña buena';
                        strengthText.className = 'text-xs text-yellow-600';
                    } else if (strength === 4) {
                        strengthText.textContent = 'Contraseña fuerte';
                        strengthText.className = 'text-xs text-green-600';
                    }
                }
            } else {
                passwordStrengthDiv.classList.add('hidden');
            }
        });
    }

    // Password match
    const password2Input = document.getElementById('password2');
    const passwordMatch = document.getElementById('password-match');
    
    if (password2Input && password1Input && passwordMatch) {
        password2Input.addEventListener('input', function() {
            const password1 = password1Input.value;
            const password2 = this.value;

            if (password2.length > 0) {
                if (password1 === password2) {
                    password2Input.classList.remove('field-error');
                    passwordMatch.textContent = '✓ Las contraseñas coinciden';
                    passwordMatch.className = 'text-xs mt-1 text-green-600';
                    passwordMatch.classList.remove('hidden');
                } else {
                    password2Input.classList.add('field-error');
                    passwordMatch.textContent = '✗ Las contraseñas no coinciden';
                    passwordMatch.className = 'text-xs mt-1 text-red-600';
                    passwordMatch.classList.remove('hidden');
                }
            } else {
                passwordMatch.classList.add('hidden');
            }
        });
    }

    // Email validation - check if exists
    const emailInput = document.getElementById('email');
    const emailFeedback = document.getElementById('email-feedback');
    
    if (emailInput && emailFeedback) {
        let emailTimeout;
        emailInput.addEventListener('input', function() {
            clearTimeout(emailTimeout);
            const email = this.value.trim();
            
            // Resetear disponibilidad mientras se escribe
            emailAvailable = false;

            if (email && email.includes('@') && email.includes('.')) {
                emailFeedback.textContent = '⏳ Verificando...';
                emailFeedback.className = 'text-xs mt-1 text-gray-600';
                emailFeedback.classList.remove('hidden');

                emailTimeout = setTimeout(() => {
                    // Verificar si el email ya existe
                    fetch('/accounts/check-email/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        body: 'email=' + encodeURIComponent(email)
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.exists) {
                            emailInput.classList.add('field-error');
                            emailFeedback.textContent = '✗ Este email ya está registrado';
                            emailFeedback.className = 'text-xs mt-1 text-red-600';
                            emailFeedback.classList.remove('hidden');
                            emailAvailable = false;
                        } else {
                            emailInput.classList.remove('field-error');
                            emailFeedback.textContent = '✓ Email disponible';
                            emailFeedback.className = 'text-xs mt-1 text-green-600';
                            emailFeedback.classList.remove('hidden');
                            emailAvailable = true;
                        }
                    })
                    .catch(error => {
                        console.error('Error checking email:', error);
                        emailFeedback.classList.add('hidden');
                    });
                }, 500);
            } else {
                emailFeedback.classList.add('hidden');
            }
        });
    }

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

    // Initialize
    showStep(1);
});
