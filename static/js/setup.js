document.addEventListener('DOMContentLoaded', function() {
  // Step navigation
  const nextButtons = document.querySelectorAll('.btn-next');
  const backButtons = document.querySelectorAll('.btn-back');
  const steps = document.querySelectorAll('.step');
  
  // API key form
  const apiKeyInput = document.getElementById('api-key-input');
  const saveApiKeyBtn = document.getElementById('save-api-key-btn');
  const apiKeyError = document.getElementById('api-key-error');
  const successMessage = document.getElementById('success-message');
  
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
  
  // Save API key
  saveApiKeyBtn.addEventListener('click', () => {
    const apiKey = apiKeyInput.value.trim();
    
    // Validate API key
    if (!apiKey) {
      showError('Please enter your API key');
      return;
    }
    
    // Additional validation for API key format (should start with 'AIza' for Google AI API keys)
    if (!apiKey.startsWith('AIza')) {
      showError('API key appears invalid. Google Gemini AI API keys typically start with "AIza".');
      return;
    }
    
    // Disable button and show loading state
    saveApiKeyBtn.disabled = true;
    saveApiKeyBtn.textContent = 'Saving...';
    hideError();
    
    // Send API key to server
    fetch('/api/save-api-key', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ api_key: apiKey })
    })
    .then(response => {
      if (!response.ok) {
        return response.json().then(data => {
          throw new Error(data.error || 'Failed to save API key');
        });
      }
      return response.json();
    })
    .then(data => {
      // Show success message
      successMessage.classList.remove('hidden');
      document.querySelector('.api-key-form').classList.add('hidden');
    })
    .catch(error => {
      console.error('Error:', error);
      showError(error.message || 'Failed to save API key. Please try again.');
    })
    .finally(() => {
      // Reset button state
      saveApiKeyBtn.disabled = false;
      saveApiKeyBtn.textContent = 'Save API Key';
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
});
