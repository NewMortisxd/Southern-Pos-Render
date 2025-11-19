document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('registerForm');
    const passwordInput = document.getElementById('id_password');
    const confirmPasswordInput = document.getElementById('id_confirm_password');
    const passwordMatchError = document.getElementById('passwordMatchError');
    const registerBtn = document.getElementById('registerBtn');

    // Password matching validation
    function validatePasswordMatch() {
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;

        if (password !== confirmPassword) {
            passwordMatchError.classList.remove('hidden');
            registerBtn.disabled = true;
            registerBtn.classList.add('opacity-50', 'cursor-not-allowed');
            return false;
        } else {
            passwordMatchError.classList.add('hidden');
            registerBtn.disabled = false;
            registerBtn.classList.remove('opacity-50', 'cursor-not-allowed');
            return true;
        }
    }

    // Add event listeners for password inputs
    passwordInput.addEventListener('input', validatePasswordMatch);
    confirmPasswordInput.addEventListener('input', validatePasswordMatch);

    // Form submission validation
    registerForm.addEventListener('submit', function(e) {
        if (!validatePasswordMatch()) {
            e.preventDefault();
        }
    });
});