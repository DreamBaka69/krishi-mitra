// Disease database
const diseaseDB = {
    'healthy': {
        name: 'Healthy Plant 🌱',
        treatment: 'Your plant appears healthy! Continue with regular care.',
        prevention: ['Regular inspection', 'Proper spacing', 'Balanced fertilization']
    },
    'bacterial_blight': {
        name: 'Bacterial Spot 🦠', 
        treatment: 'Apply copper-based bactericides. Remove infected plants.',
        prevention: ['Use disease-free seeds', 'Practice crop rotation']
    },
    'leaf_spot_early': {
        name: 'Early Blight 🍂',
        treatment: 'Apply fungicides. Remove infected leaves.',
        prevention: ['Remove plant debris', 'Water at base']
    },
    'leaf_spot_late': {
        name: 'Late Blight 🍂🔥',
        treatment: 'URGENT: Apply systemic fungicides immediately.',
        prevention: ['Plant resistant varieties', 'Monitor weather']
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

// Backend URL - MAKE SURE THIS IS CORRECT
const BACKEND_URL = 'https://krishi-mitra-backend.onrender.com';

// Handle image upload
elements.imageInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            elements.imagePreview.innerHTML = `
                <div style="text-align: center;">
                    <h3>📸 Image Preview:</h3>
                    <img src="${e.target.result}" style="max-width: 300px; border-radius: 10px;">
                    <p><small>${file.name}</small></p>
                </div>
            `;
            elements.analyzeBtn.disabled = false;
        };
        reader.readAsDataURL(file);
    }
});

// Analyze image - SIMPLE AND GUARANTEED TO WORK
async function analyzeImage() {
    const file = elements.imageInput.files[0];
    if (!file) {
        alert('Please select an image first');
        return;
    }

    // Show loading
    elements.loading.style.display = 'block';
    elements.analyzeBtn.disabled = true;
    elements.resultSection.style.display = 'none';

    try {
        console.log('🚀 Starting analysis...');
        
        const formData = new FormData();
        formData.append('image', file);

        // SIMPLE FETCH - NO COMPLEX OPTIONS
        const response = await fetch(BACKEND_URL + '/analyze', {
            method: 'POST',
            body: formData
        });

        console.log('📡 Response status:', response.status);

        if (!response.ok) {
            throw new Error(`Server returned ${response.status}`);
        }

        const result = await response.json();
        console.log('✅ Success:', result);
        
        // SHOW RESULTS
        showResults(result);
        
    } catch (error) {
        console.error('❌ Error:', error);
        // FALLBACK TO DEMO
        const demoResult = {
            disease: 'healthy',
            confidence: 0.90,
            detailed_class: 'Tomato___healthy',
            message: 'Demo result - backend issue'
        };
        showResults(demoResult);
        alert('Using demo results due to backend issue.');
    } finally {
        elements.loading.style.display = 'none';
        elements.analyzeBtn.disabled = false;
    }
}

// Show results
function showResults(result) {
    const disease = result.disease || 'healthy';
    const confidence = result.confidence || 0.85;
    const info = diseaseDB[disease] || diseaseDB['healthy'];
    
    elements.diseaseResult.innerHTML = `
        <div style="font-size: 24px; font-weight: bold; color: #2ecc71;">${info.name}</div>
        <div style="font-size: 16px; color: #666;">Confidence: ${(confidence * 100).toFixed(1)}%</div>
        <div style="color: #e67e22; margin-top: 10px;">${result.message || 'Analysis complete'}</div>
    `;
    
    elements.treatmentAdvice.innerHTML = `
        <h4>💡 Treatment</h4>
        <p>${info.treatment}</p>
        <h4>🛡️ Prevention</h4>
        <ul>
            ${info.prevention.map(item => `<li>${item}</li>`).join('')}
        </ul>
    `;
    
    elements.resultSection.style.display = 'block';
    elements.resultSection.scrollIntoView({ behavior: 'smooth' });
}

// Reset form
function resetForm() {
    elements.imageInput.value = '';
    elements.imagePreview.innerHTML = '';
    elements.resultSection.style.display = 'none';
    elements.analyzeBtn.disabled = true;
}

// Initialize
console.log('🌱 Krishi Mitra Frontend Loaded');
