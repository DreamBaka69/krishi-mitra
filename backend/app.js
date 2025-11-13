// Disease database
const diseaseDB = {
    'healthy': {
        name: 'Healthy Plant 🌱',
        treatment: 'Your tomato plant appears healthy! Continue with regular care including proper watering, balanced fertilization, and regular monitoring.',
        prevention: [
            'Regular plant inspection',
            'Proper spacing between plants',
            'Balanced NPK fertilization',
            'Adequate sunlight exposure',
            'Crop rotation practices'
        ]
    },
    'bacterial_blight': {
        name: 'Bacterial Spot 🦠',
        treatment: 'Apply copper-based bactericides like Copper Oxychloride. Remove and destroy severely infected plants. Avoid overhead watering to prevent spread.',
        prevention: [
            'Use disease-free seeds',
            'Avoid working with wet plants',
            'Practice crop rotation',
            'Ensure good air circulation',
            'Disinfect gardening tools'
        ]
    },
    'leaf_spot_early': {
        name: 'Early Blight 🍂',
        treatment: 'Apply fungicides containing Chlorothalonil or Mancozeb. Remove infected leaves. Improve air circulation and avoid wetting foliage.',
        prevention: [
            'Remove plant debris regularly',
            'Water at base of plants',
            'Use resistant varieties',
            'Proper plant spacing',
            'Avoid overhead irrigation'
        ]
    },
    'leaf_spot_late': {
        name: 'Late Blight 🍂🔥',
        treatment: 'URGENT: Apply systemic fungicides like Metalaxyl. Remove and destroy all infected plants immediately. This disease spreads rapidly.',
        prevention: [
            'Plant resistant varieties',
            'Avoid overhead watering',
            'Remove volunteer plants',
            'Monitor weather conditions',
            'Use protective fungicides preventively'
        ]
    }
};

// DOM elements
const elements = {
    imageInput: document.getElementById('imageInput'),
    analyzeBtn: document.getElementById('analyzeBtn'),
    imagePreview: document.getElementById('imagePreview'),
    resultSection: document.getElementById('resultSection'),
    diseaseResult: document.getElementById('diseaseResult'),
    treatmentAdvice: document.getElementById('treatmentAdvice'),
    loading: document.getElementById('loading')
};

// Backend configuration - FIXED URL
const CONFIG = {
    BACKEND_URL: 'https://krishi-mitra-backend.onrender.com', // CORRECT BACKEND URL
    TIMEOUT: 30000
};

// Handle image upload
elements.imageInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        // Validate file type
        if (!file.type.match('image.*')) {
            alert('Please upload an image file (JPG, PNG, JPEG)');
            return;
        }
        
        // Validate file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
            alert('Please upload an image smaller than 5MB');
            return;
        }
        
        const reader = new FileReader();
        reader.onload = function(e) {
            elements.imagePreview.innerHTML = `
                <div class="preview-container">
                    <h3>📸 Image Preview:</h3>
                    <img src="${e.target.result}" class="preview-img" alt="Crop Image Preview">
                </div>
            `;
            elements.analyzeBtn.disabled = false;
        };
        reader.readAsDataURL(file);
    }
});

// Check backend health
async function checkBackendHealth() {
    try {
        console.log(`🔍 Checking backend at: ${CONFIG.BACKEND_URL}/health`);
        
        const response = await fetch(`${CONFIG.BACKEND_URL}/health`, {
            method: 'GET',
            mode: 'cors'
        });

        if (response.ok) {
            const data = await response.json();
            console.log('✅ Backend health:', data);
            return true;
        }
        return false;
    } catch (error) {
        console.log('❌ Backend health check failed:', error);
        return false;
    }
}

// Update connection status
function updateConnectionStatus(isConnected) {
    let statusDiv = document.getElementById('connection-status');
    
    if (!isConnected) {
        if (!statusDiv) {
            statusDiv = document.createElement('div');
            statusDiv.id = 'connection-status';
            statusDiv.innerHTML = `
                <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; margin: 10px 0; border-radius: 5px; text-align: center;">
                    <strong>⚠️ Demo Mode:</strong> Backend connection failed. Using simulated results.
                </div>
            `;
            const container = document.querySelector('.container');
            if (container) {
                container.insertBefore(statusDiv, container.firstChild);
            }
        }
    } else if (statusDiv) {
        statusDiv.remove();
    }
}

// Analyze image function
async function analyzeImage() {
    const file = elements.imageInput.files[0];
    if (!file) {
        alert('Please select an image first');
        return;
    }

    showLoading(true);
    
    try {
        const formData = new FormData();
        formData.append('image', file);

        console.log(`🔄 Sending to: ${CONFIG.BACKEND_URL}/analyze`);

        const response = await fetch(`${CONFIG.BACKEND_URL}/analyze`, {
            method: 'POST',
            body: formData,
            mode: 'cors'
        });

        console.log('📡 Response status:', response.status);

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Server error: ${response.status} - ${errorText}`);
        }

        const result = await response.json();
        console.log('✅ Analysis result:', result);
        
        if (result.error) {
            throw new Error(result.error);
        }
        
        updateConnectionStatus(true);
        showResults(result);
        
    } catch (error) {
        console.error('❌ Analysis failed:', error);
        updateConnectionStatus(false);
        
        // Show error but continue with demo
        const mockResult = getMockResult();
        showResults(mockResult);
        
        // Show error message
        setTimeout(() => {
            alert(`Analysis failed: ${error.message}. Showing demo results.`);
        }, 100);
    } finally {
        showLoading(false);
    }
}

// Show loading state
function showLoading(show) {
    elements.loading.style.display = show ? 'block' : 'none';
    elements.analyzeBtn.disabled = show;
    if (show) {
        elements.resultSection.style.display = 'none';
    }
}

// Display results
function showResults(result) {
    const disease = result.disease || 'healthy';
    const confidence = result.confidence || 0.85;
    const detailedClass = result.detailed_class || disease;
    const isDemo = result.note && result.note.includes('Demo');
    
    const info = diseaseDB[disease] || diseaseDB['healthy'];
    
    elements.diseaseResult.innerHTML = `
        <div class="disease-name">${info.name}</div>
        <div class="confidence">Confidence: ${(confidence * 100).toFixed(1)}%</div>
        <div class="disease-detail">Detected: ${formatDiseaseName(detailedClass)}</div>
        ${isDemo ? '<div style="color: #e67e22; margin-top: 10px;">🔮 Demo Result</div>' : '<div style="color: #27ae60; margin-top: 10px;">✅ Real Analysis</div>'}
    `;
    
    elements.treatmentAdvice.innerHTML = `
        <h4>💡 Treatment Recommendation</h4>
        <p>${info.treatment}</p>
        
        <h4>🛡️ Preventive Measures</h4>
        <ul>
            ${info.prevention.map(item => `<li
