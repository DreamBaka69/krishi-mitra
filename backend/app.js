// Disease database - Updated for PlantVillage dataset
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

// Backend configuration
const CONFIG = {
    BACKEND_URL: 'https://krishi-mitra-backend.onrender.com',
    TIMEOUT: 30000, // 30 seconds
    MAX_RETRIES: 2
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
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000);

        const response = await fetch(`${CONFIG.BACKEND_URL}/health`, {
            method: 'GET',
            signal: controller.signal,
            mode: 'cors'
        });

        clearTimeout(timeoutId);
        return response.ok;
    } catch (error) {
        console.log('Backend health check failed:', error);
        return false;
    }
}

// Update connection status display
function updateConnectionStatus(isConnected) {
    const existingStatus = document.getElementById('connection-status');
    if (existingStatus) {
        existingStatus.remove();
    }
    
    if (!isConnected) {
        const statusDiv = document.createElement('div');
        statusDiv.id = 'connection-status';
        statusDiv.innerHTML = `
            <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; margin: 10px 0; border-radius: 5px; text-align: center;">
                <strong>⚠️ Demo Mode:</strong> Using simulated results. Real analysis will resume when backend is available.
            </div>
        `;
        // Insert at the top of the main content
        const mainContent = document.querySelector('.container') || document.body;
        mainContent.insertBefore(statusDiv, mainContent.firstChild);
    }
}

// Analyze image function
async function analyzeImage() {
    const file = elements.imageInput.files[0];
    if (!file) return;

    showLoading(true);
    
    try {
        const formData = new FormData();
        formData.append('image', file);

        // Add timeout and better error handling
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), CONFIG.TIMEOUT);

        const response = await fetch(`${CONFIG.BACKEND_URL}/analyze`, {
            method: 'POST',
            body: formData,
            signal: controller.signal,
            mode: 'cors'
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            // Handle specific HTTP errors
            if (response.status === 503) {
                throw new Error('Backend service is temporarily unavailable. Please try again in a few minutes.');
            } else if (response.status === 500) {
                throw new Error('Internal server error. The model might be loading.');
            } else if (response.status === 400) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Invalid request');
            }
            throw new Error(`Server error: ${response.status} ${response.statusText}`);
        }

        const result = await response.json();
        
        if (result.error) {
            throw new Error(result.error);
        }
        
        // Update connection status
        updateConnectionStatus(true);
        showResults(result);
        
    } catch (error) {
        console.error('Analysis error:', error);
        
        // Update connection status
        updateConnectionStatus(false);
        
        // More specific error messages
        if (error.name === 'AbortError') {
            alert('Request timeout. The server is taking too long to respond. Please try again.');
        } else if (error.message.includes('Failed to fetch') || error.message.includes('CORS')) {
            alert('Cannot connect to the analysis server. This might be due to server maintenance. Using demo mode for now.');
        } else {
            alert(`Analysis failed: ${error.message}. Using demo mode.`);
        }
        
        // Fallback to mock result for demo
        const mockResult = getMockResult();
        showResults(mockResult);
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
        ${isDemo ? '<div style="color: #e67e22; margin-top: 10px;">🔮 Demo Result - Backend Unavailable</div>' : ''}
    `;
    
    elements.treatmentAdvice.innerHTML = `
        <h4>💡 Treatment Recommendation</h4>
        <p>${info.treatment}</p>
        
        <h4>🛡️ Preventive Measures</h4>
        <ul>
            ${info.prevention.map(item => `<li>${item}</li>`).join('')}
        </ul>
        
        <div style="margin-top: 20px; padding: 15px; background: #fff3cd; border-radius: 8px; border-left: 4px solid #ffc107;">
            <strong>⚠️ Important:</strong> For severe infections, consult local agricultural experts for specific treatment plans.
        </div>
    `;
    
    elements.resultSection.style.display = 'block';
    
    // Scroll to results
    elements.resultSection.scrollIntoView({ behavior: 'smooth' });
}

// Format disease names for display
function formatDiseaseName(className) {
    return className.replace(/_/g, ' ').replace('Tomato ', '');
}

// Mock result for demo when backend is not available
function getMockResult() {
    const diseases = ['healthy', 'bacterial_blight', 'leaf_spot_early', 'leaf_spot_late'];
    const randomDisease = diseases[Math.floor(Math.random() * diseases.length)];
    
    // Map to PlantVillage class names for realism
    const classMap = {
        'healthy': 'Tomato___healthy',
        'bacterial_blight': 'Tomato___Bacterial_spot',
        'leaf_spot_early': 'Tomato___Early_blight',
        'leaf_spot_late': 'Tomato___Late_blight'
    };
    
    return {
        disease: randomDisease,
        confidence: 0.75 + Math.random() * 0.2,
        detailed_class: classMap[randomDisease],
        note: 'Demo mode - backend unavailable'
    };
}

// Reset form
function resetForm() {
    elements.imageInput.value = '';
    elements.imagePreview.innerHTML = '';
    elements.resultSection.style.display = 'none';
    elements.analyzeBtn.disabled = true;
    
    // Remove connection status
    const existingStatus = document.getElementById('connection-status');
    if (existingStatus) {
        existingStatus.remove();
    }
}

// Initialize app with health check
async function initializeApp() {
    console.log('🌱 Krishi Mitra Frontend Loaded');
    
    const isBackendHealthy = await checkBackendHealth();
    if (!isBackendHealthy) {
        console.warn('⚠️ Backend service appears to be unavailable');
        updateConnectionStatus(false);
    } else {
        console.log('✅ Backend service is healthy');
        updateConnectionStatus(true);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeApp);
