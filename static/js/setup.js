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
  
  function showError(message) {
    apiKeyError.textContent = message;
    apiKeyError.classList.remove('hidden');
  }
  
  function hideError() {
    apiKeyError.classList.add('hidden');
  }
});
