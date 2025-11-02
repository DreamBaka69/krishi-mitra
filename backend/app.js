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

// Analyze image function
async function analyzeImage() {
    const file = elements.imageInput.files[0];
    if (!file) return;

    showLoading(true);
    
    try {
        const formData = new FormData();
        formData.append('image', file);

        
        const BACKEND_URL = 'https://krishi-mitra-backend.onrender.com';
        const response = await fetch(`${BACKEND_URL}/analyze`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const result = await response.json();
        
        if (result.error) {
            throw new Error(result.error);
        }
        
        showResults(result);
        
    } catch (error) {
        console.error('Analysis error:', error);
        alert('Failed to analyze image. Please try again or check if the server is running.');
        // Fallback for demo
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
    
    const info = diseaseDB[disease] || diseaseDB['healthy'];
    
    elements.diseaseResult.innerHTML = `
        <div class="disease-name">${info.name}</div>
        <div class="confidence">Confidence: ${(confidence * 100).toFixed(1)}%</div>
        <div class="disease-detail">Detected: ${formatDiseaseName(detailedClass)}</div>
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
        detailed_class: classMap[randomDisease]
    };
}

// Reset form
function resetForm() {
    elements.imageInput.value = '';
    elements.imagePreview.innerHTML = '';
    elements.resultSection.style.display = 'none';
    elements.analyzeBtn.disabled = true;
}

// Add some sample images for demo (optional)
function addSampleImages() {
    // This would be implemented if you have sample images
    console.log('Sample images feature ready');
}

// Initialize app
console.log('🌱 Krishi Mitra Frontend Loaded');
console.log('Make sure backend is running on http://localhost:5000');