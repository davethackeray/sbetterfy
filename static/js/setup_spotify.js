document.addEventListener('DOMContentLoaded', function() {
    // Step navigation
    const nextButtons = document.querySelectorAll('.btn-next');
    const backButtons = document.querySelectorAll('.btn-back');
    
    // Spotify credentials form
    const clientIdInput = document.getElementById('client-id-input');
    const clientSecretInput = document.getElementById('client-secret-input');
    const saveCredsBtn = document.getElementById('save-spotify-creds-btn');
    const credsError = document.getElementById('spotify-creds-error');
    const successMessage = document.getElementById('spotify-success-message');
    
    // Next step buttons
    nextButtons.forEach(button => {
        button.addEventListener('click', () => {
            const currentStep = button.closest('.step');
            const nextStepId = button.dataset.next;
            const nextStep = document.getElementById(nextStepId);
            
            currentStep.classList.add('hidden');
            nextStep.classList.remove('hidden');
        });
    });
    
    // Back buttons
    backButtons.forEach(button => {
        button.addEventListener('click', () => {
            const currentStep = button.closest('.step');
            const prevStepId = button.dataset.prev;
            const prevStep = document.getElementById(prevStepId);
            
            currentStep.classList.add('hidden');
            prevStep.classList.remove('hidden');
        });
    });
    
    // Save Spotify credentials
    saveCredsBtn.addEventListener('click', () => {
        const clientId = clientIdInput.value.trim();
        const clientSecret = clientSecretInput.value.trim();
        
        // Validate inputs
        if (!clientId || !clientSecret) {
            showError('Please enter both Client ID and Client Secret');
            return;
        }
        
        // Disable button and show loading state
        saveCredsBtn.disabled = true;
        saveCredsBtn.textContent = 'Saving...';
        hideError();
        
        // Send credentials to server
        fetch('/api/save-spotify-creds', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                client_id: clientId,
                client_secret: clientSecret
            })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Failed to save Spotify credentials');
                });
            }
            return response.json();
        })
        .then(data => {
            // Show success message
            successMessage.classList.remove('hidden');
            document.querySelector('.spotify-creds-form').classList.add('hidden');
        })
        .catch(error => {
            console.error('Error:', error);
            showError(error.message || 'Failed to save credentials. Please try again.');
        })
        .finally(() => {
            // Reset button state
            saveCredsBtn.disabled = false;
            saveCredsBtn.textContent = 'Save Credentials';
        });
    });
    
    function showError(message) {
        credsError.textContent = message;
        credsError.classList.remove('hidden');
    }
    
    function hideError() {
        credsError.classList.add('hidden');
    }
    
    // Check if credentials are already set
    fetch('/api/validate-spotify-creds')
        .then(response => response.json())
        .then(data => {
            if (data.valid) {
                // Skip to success state
                document.querySelector('.spotify-creds-form').classList.add('hidden');
                successMessage.classList.remove('hidden');
            }
        })
        .catch(error => {
            console.error('Error checking credentials:', error);
        });
});
