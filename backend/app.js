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

// Backend configuration
const CONFIG = {
    BACKEND_URL: 'https://krishi-mitra-backend.onrender.com'
};

// Handle image upload
elements.imageInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        // Basic validation
        if (!file.type.match('image.*')) {
            alert('Please upload an image file (JPG, PNG, JPEG)');
            this.value = '';
            return;
        }
        
        if (file.size > 5 * 1024 * 1024) {
            alert('Please upload an image smaller than 5MB');
            this.value = '';
            return;
        }
        
        const reader = new FileReader();
        reader.onload = function(e) {
            elements.imagePreview.innerHTML = `
                <div class="preview-container">
                    <h3>📸 Image Preview:</h3>
                    <img src="${e.target.result}" class="preview-img" alt="Crop Image Preview">
                    <p><small>File: ${file.name} (${(file.size/1024).toFixed(1)} KB)</small></p>
                </div>
            `;
            elements.analyzeBtn.disabled = false;
        };
        reader.readAsDataURL(file);
    }
});

// Check backend connection
async function checkBackendConnection() {
    try {
        console.log('🔍 Checking backend connection...');
        const response = await fetch(`${CONFIG.BACKEND_URL}/health`);
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Backend connected:', data);
            return true;
        }
        return false;
    } catch (error) {
        console.log('❌ Backend connection failed:', error.message);
        return false;
    }
}

// Update connection status
function updateConnectionStatus(isConnected) {
    let statusDiv = document.getElementById('connection-status');
    
    if (!isConnected && !statusDiv) {
        statusDiv = document.createElement('div');
        statusDiv.id = 'connection-status';
        statusDiv.innerHTML = `
            <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; margin: 10px 0; border-radius: 5px; text-align: center;">
                <strong>⚠️ Demo Mode:</strong> Backend connection failed. Using simulated results.
            </div>
        `;
        const container = document.querySelector('.container');
        if (container) container.insertBefore(statusDiv, container.firstChild);
    } else if (isConnected && statusDiv) {
        statusDiv.remove();
    }
}

// Analyze image - SIMPLIFIED AND GUARANTEED TO WORK
async function analyzeImage() {
    const file = elements.imageInput.files[0];
    if (!file) {
        alert('Please select an image first');
        return;
    }

    showLoading(true);
    
    try {
        console.log('🚀 Starting analysis...');
        
        // First check if backend is reachable
        const isBackendAlive = await checkBackendConnection();
        
        if (!isBackendAlive) {
            throw new Error('Backend server is not responding');
        }
        
        // Send to backend
        const formData = new FormData();
        formData.append('image', file);

        console.log('🔄 Sending to backend...');
        
        const response = await fetch(`${CONFIG.BACKEND_URL}/analyze`, {
            method: 'POST',
            body: formData
        });

        console.log('📡 Response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const result = await response.json();
        console.log('✅ Backend result:', result);
        
        if (result.error) {
            throw new Error(result.error);
        }
        
        // SUCCESS - Show real results
        updateConnectionStatus(true);
        showResults(result);
        
    } catch (error) {
        console.error('❌ Using demo mode:', error);
        
        // FALLBACK: Always show demo results
        updateConnectionStatus(false);
        const mockResult = getMockResult(file.name);
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
        ${isDemo ? 
            '<div style="color: #e67e22; margin-top: 10px;">🔮 Demo Result</div>' : 
            '<div style="color: #27ae60; margin-top: 10px;">✅ Real Analysis</div>'
        }
    `;
    
    elements.treatmentAdvice.innerHTML = `
        <h4>💡 Treatment Recommendation</h4>
        <p>${info.treatment}</p>
        
        <h4>🛡️ Preventive Measures</h4>
        <ul>
            ${info.prevention.map(item => `<li>${item}</li>`).join('')}
        </ul>
        
        <div style="margin-top: 20px; padding: 15px; background: #fff3cd; border-radius: 8px; border-left: 4px solid #ffc107;">
            <strong>⚠️ Important:</strong> For accurate diagnosis, consult agricultural experts.
        </div>
    `;
    
    elements.resultSection.style.display = 'block';
    elements.resultSection.scrollIntoView({ behavior: 'smooth' });
}

// Format disease names
function formatDiseaseName(className) {
    return className.replace(/_/g, ' ').replace('Tomato ', '');
}

// Demo result generator
function getMockResult(filename) {
    const diseases = ['healthy', 'bacterial_blight', 'leaf_spot_early', 'leaf_spot_late'];
    const randomDisease = diseases[Math.floor(Math.random() * diseases.length)];
    
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
        note: 'Demo analysis'
    };
}

// Reset form
function resetForm() {
    elements.imageInput.value = '';
    elements.imagePreview.innerHTML = '';
    elements.resultSection.style.display = 'none';
    elements.analyzeBtn.disabled = true;
    
    const statusDiv = document.getElementById('connection-status');
    if (statusDiv) statusDiv.remove();
}

// Initialize app
async function initializeApp() {
    console.log('🌱 Krishi Mitra Frontend Loaded');
    
    const isConnected = await checkBackendConnection();
    updateConnectionStatus(isConnected);
    
    if (isConnected) {
        console.log('✅ Backend connection: SUCCESS');
    } else {
        console.log('⚠️ Backend connection: FAILED - Using demo mode');
    }
}

// Start application
document.addEventListener('DOMContentLoaded', initializeApp);
