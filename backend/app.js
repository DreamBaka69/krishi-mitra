// Disease database
const diseaseDB = {
    'healthy': {
        name: 'Healthy Plant 🌱',
        treatment: 'Your plant appears healthy! Continue with regular care including proper watering, balanced fertilization, and regular monitoring. Maintain good plant hygiene and ensure adequate sunlight exposure.',
        prevention: [
            'Regular plant inspection for early signs',
            'Proper spacing between plants for air circulation',
            'Balanced NPK fertilization',
            'Adequate sunlight exposure',
            'Crop rotation practices',
            'Proper watering schedule'
        ]
    },
    'bacterial_blight': {
        name: 'Bacterial Spot 🦠',
        treatment: 'Apply copper-based bactericides like Copper Oxychloride. Remove and destroy severely infected plants. Avoid overhead watering to prevent spread. Isolate affected plants immediately.',
        prevention: [
            'Use certified disease-free seeds',
            'Avoid working with wet plants',
            'Practice 3-year crop rotation',
            'Ensure good air circulation',
            'Disinfect gardening tools regularly',
            'Remove plant debris after harvest'
        ]
    },
    'leaf_spot_early': {
        name: 'Early Blight 🍂',
        treatment: 'Apply fungicides containing Chlorothalonil or Mancozeb. Remove infected leaves promptly. Improve air circulation and avoid wetting foliage. Apply treatments every 7-10 days.',
        prevention: [
            'Remove plant debris regularly',
            'Water at base of plants only',
            'Use resistant varieties when available',
            'Proper plant spacing (18-24 inches)',
            'Avoid overhead irrigation',
            'Stake plants for better air flow'
        ]
    },
    'leaf_spot_late': {
        name: 'Late Blight 🍂🔥',
        treatment: 'URGENT: Apply systemic fungicides like Metalaxyl or Fosetyl-Al. Remove and destroy all infected plants immediately. This disease spreads rapidly in cool, wet conditions.',
        prevention: [
            'Plant resistant varieties',
            'Avoid overhead watering',
            'Remove volunteer plants and weeds',
            'Monitor weather conditions closely',
            'Use protective fungicides preventively',
            'Ensure excellent drainage'
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
    TIMEOUT: 30000
};

// Handle image upload
elements.imageInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        // Validate file type
        if (!file.type.match('image.*')) {
            alert('Please upload an image file (JPG, PNG, JPEG)');
            this.value = '';
            return;
        }
        
        // Validate file size (max 5MB)
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
        
        reader.onerror = function() {
            alert('Error reading image file. Please try another image.');
            elements.imageInput.value = '';
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

    console.log('🚀 Starting analysis with file:', file.name);
    showLoading(true);
    
    try {
        const formData = new FormData();
        formData.append('image', file);

        console.log(`🔄 Sending to backend: ${CONFIG.BACKEND_URL}/analyze`);

        const response = await fetch(`${CONFIG.BACKEND_URL}/analyze`, {
            method: 'POST',
            body: formData
        });

        console.log('📡 Response status:', response.status);

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const result = await response.json();
        console.log('✅ Backend analysis result:', result);
        
        if (result.error) {
            throw new Error(result.error);
        }
        
        updateConnectionStatus(true);
        showResults(result);
        
    } catch (error) {
        console.error('❌ Analysis failed:', error);
        updateConnectionStatus(false);
        
        // Fallback to demo result
        const mockResult = getMockResult();
        showResults(mockResult);
        
        setTimeout(() => {
            alert(`Backend analysis failed: ${error.message}\nShowing demo results for testing.`);
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
    const isDemo = result.message && result.message.includes('Demo');
    
    const info = diseaseDB[disease] || diseaseDB['healthy'];
    
    elements.diseaseResult.innerHTML = `
        <div class="disease-name">${info.name}</div>
        <div class="confidence">Confidence: ${(confidence * 100).toFixed(1)}%</div>
        <div class="disease-detail">Detected: ${formatDiseaseName(detailedClass)}</div>
        ${isDemo ? 
            '<div style="color: #e67e22; margin-top: 10px;">🔮 Demo Result - Backend Unavailable</div>' : 
            '<div style="color: #27ae60; margin-top: 10px;">✅ Real Backend Analysis</div>'
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
            <strong>⚠️ Important:</strong> For severe infections or uncertain diagnoses, consult local agricultural experts for specific treatment plans.
        </div>
    `;
    
    elements.resultSection.style.display = 'block';
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
    
    const statusDiv = document.getElementById('connection-status');
    if (statusDiv) {
        statusDiv.remove();
    }
}

// Initialize app
async function initializeApp() {
    console.log('🌱 Krishi Mitra Frontend Loaded');
    console.log(`🔗 Backend URL: ${CONFIG.BACKEND_URL}`);
    
    const isHealthy = await checkBackendConnection();
    updateConnectionStatus(isHealthy);
    
    if (isHealthy) {
        console.log('✅ Backend connection successful');
    } else {
        console.log('⚠️ Backend unavailable - demo mode active');
    }
}

// Start when page loads
document.addEventListener('DOMContentLoaded', initializeApp);
