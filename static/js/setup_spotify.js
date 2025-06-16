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
        
        // Additional validation for Client ID format (should be a 32-character hexadecimal string)
        if (!/^[0-9a-fA-F]{32}$/.test(clientId)) {
            showError('Client ID must be a 32-character hexadecimal string');
            return;
        }
        
        // Additional validation for Client Secret format (should be a 32-character hexadecimal string)
        if (!/^[0-9a-fA-F]{32}$/.test(clientSecret)) {
            showError('Client Secret must be a 32-character hexadecimal string');
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
    
function showFlashMessage(message, type = 'error') {
    const container = document.getElementById('flash-messages') || createFlashContainer();
    const messageElement = document.createElement('div');
    messageElement.className = `flash-message ${type}`;
    messageElement.textContent = message;
    container.appendChild(messageElement);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        messageElement.remove();
    }, 5000);
}

function createFlashContainer() {
    const container = document.createElement('div');
    container.id = 'flash-messages';
    container.style.position = 'fixed';
    container.style.top = '20px';
    container.style.right = '20px';
    container.style.zIndex = '1000';
    document.body.appendChild(container);
    return container;
}

function showError(message) {
    showFlashMessage(message, 'error');
}

function hideError() {
    // No action needed as flash messages auto-dismiss
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
