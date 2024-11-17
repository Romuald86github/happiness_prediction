// Form submission handler
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('predictionForm');
    const resultDiv = document.getElementById('result');
    const errorDiv = document.getElementById('error');
    const errorMessage = document.getElementById('errorMessage');
    const predictionValue = document.getElementById('predictionValue');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Show loading state
        const submitButton = e.target.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.textContent;
        submitButton.disabled = true;
        submitButton.textContent = 'Predicting...';
        
        // Hide previous results/errors
        resultDiv.classList.add('hidden');
        errorDiv.classList.add('hidden');
        
        try {
            // Collect and validate form data
            const formData = new FormData(e.target);
            const data = {};
            let hasError = false;
            
            for (let [key, value] of formData.entries()) {
                const floatValue = parseFloat(value);
                if (isNaN(floatValue)) {
                    showError(`Invalid value for ${key}`);
                    hasError = true;
                    break;
                }
                if (floatValue < -1000 || floatValue > 1000) {
                    showError(`Value for ${key} must be between -1000 and 1000`);
                    hasError = true;
                    break;
                }
                data[key] = floatValue;
            }
            
            if (!hasError) {
                // Make prediction request
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const result = await response.json();
                
                if (result.success) {
                    // Show prediction
                    predictionValue.textContent = result.prediction;
                    resultDiv.classList.remove('hidden');
                } else {
                    showError(result.error || 'Prediction failed');
                }
            }
        } catch (error) {
            console.error('Prediction error:', error);
            showError('An error occurred. Please try again.');
        } finally {
            // Restore button state
            submitButton.disabled = false;
            submitButton.textContent = originalButtonText;
        }
    });

    // Add input validation
    document.querySelectorAll('input[type="number"]').forEach(input => {
        input.addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            if (isNaN(value)) {
                e.target.setCustomValidity('Please enter a valid number');
            } else if (value < -1000 || value > 1000) {
                e.target.setCustomValidity('Value must be between -1000 and 1000');
            } else {
                e.target.setCustomValidity('');
            }
        });
        
        // Add blur event to format number
        input.addEventListener('blur', (e) => {
            const value = parseFloat(e.target.value);
            if (!isNaN(value)) {
                e.target.value = value.toFixed(2);
            }
        });
    });

    function showError(message) {
        errorMessage.textContent = message;
        errorDiv.classList.remove('hidden');
        // Scroll error into view
        errorDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
});