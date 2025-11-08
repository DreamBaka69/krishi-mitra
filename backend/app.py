from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Enable CORS for all origins
CORS(app)

# Global variable for model (we'll add this later)
model = None

@app.route('/')
def home():
    return jsonify({"message": "🌱 Krishi Mitra Backend is LIVE!"})

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "krishi_mitra_backend", 
        "timestamp": datetime.now().isoformat(),
        "model_loaded": model is not None,
        "environment": "production"
    })

@app.route('/test')
def test():
    return jsonify({
        "message": "✅ Backend is working!",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/classes')
def classes():
    return jsonify({
        "classes": [
            "Tomato___healthy", 
            "Tomato___Early_blight", 
            "Tomato___Late_blight",
            "Tomato___Bacterial_spot"
        ],
        "simple_mapping": {
            "Tomato___healthy": "healthy",
            "Tomato___Early_blight": "leaf_spot_early", 
            "Tomato___Late_blight": "leaf_spot_late",
            "Tomato___Bacterial_spot": "bacterial_blight"
        },
        "total_classes": 4,
        "status": "demo"
    })

@app.route('/analyze', methods=['POST', 'OPTIONS'])
def analyze():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        # Basic file validation
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        logger.info(f"📸 Received image: {file.filename}")
        
        # Return a successful demo response
        demo_result = {
            "disease": "healthy",
            "confidence": 0.89,
            "detailed_class": "Tomato___healthy",
            "note": "Demo analysis - AI model not loaded",
            "filename": file.filename,
            "file_size": len(file.read()) if file else 0
        }
        
        return jsonify(demo_result)
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return jsonify({
            "error": f"Analysis failed: {str(e)}",
            "disease": "healthy",
            "confidence": 0.75,
            "detailed_class": "Tomato___healthy",
            "note": "Fallback due to error"
        })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🚀 Starting Krishi Mitra backend on port {port}")
    print(f"🌱 Krishi Mitra Backend Running on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
