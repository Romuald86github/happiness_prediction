// Form submission handler
document.getElementById('predictionForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Show loading state
    const submitButton = e.target.querySelector('button[type="submit"]');
    const originalButtonText = submitButton.textContent;
    submitButton.disabled = true;
    submitButton.textContent = 'Predicting...';
    
    // Hide previous results/errors
    document.getElementById('result').classList.add('hidden');
    document.getElementById('error').classList.add('hidden');
    
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
            
            const result = await response.json();
            
            if (result.success) {
                // Show prediction
                document.getElementById('predictionValue').textContent = result.prediction;
                document.getElementById('result').classList.remove('hidden');
            } else {
                showError(result.error || 'Prediction failed');
            }
        }
    } catch (error) {
        showError('An error occurred. Please try again.');
        console.error('Prediction error:', error);
    } finally {
        // Restore button state
        submitButton.disabled = false;
        submitButton.textContent = originalButtonText;
    }
});

function showError(message) {
    const errorDiv = document.getElementById('error');
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.textContent = message;
    errorDiv.classList.remove('hidden');
}

// Add input validation
document.querySelectorAll('input[type="number"]').forEach(input => {
    input.addEventListener('input', (e) => {
        const value = parseFloat(e.target.value);
        if (!isNaN(value) && (value < -1000 || value > 1000)) {
            e.target.setCustomValidity('Value must be between -1000 and 1000');
        } else {
            e.target.setCustomValidity('');
        }
    });
});