import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from model import CropDiseaseModel
from PIL import Image
import io
import logging
from datetime import datetime

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('krishi_mitra')

def ensure_model_exists():
    model_path = 'crop_disease_model.h5'
    if not os.path.exists(model_path):
        logger.info("📥 Model not found, attempting to download...")
        try:
            from download_model import download_model
            download_model()
            if os.path.exists(model_path):
                logger.info("✅ Model downloaded successfully!")
            else:
                logger.warning("❌ Model download failed, using demo mode")
        except Exception as e:
            logger.error(f"❌ Download failed: {e}")

ensure_model_exists()

# Create Flask app
app = Flask(__name__)

# Configure CORS - FIXED ORIGIN
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://krishi-mitra-crob.onrender.com",  # FIXED TYPO: was krish-mitra
            "https://DreamBaka69.github.io",
            "http://localhost:3000",
            "http://127.0.0.1:3000", 
            "http://localhost:5000",
            "http://127.0.0.1:5000"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
        "supports_credentials": True
    }
})

# Initialize AI model
try:
    logger.info("🌱 Starting Krishi Mitra Server...")
    model = CropDiseaseModel('crop_disease_model.h5')
    logger.info("🚀 AI Model initialized successfully!")
except Exception as e:
    logger.error(f"❌ Failed to initialize model: {e}")
    model = None

# Serve frontend files 
@app.route('/')
def serve_frontend():
    """Serve the main frontend page"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static_files(filename):
    """Serve CSS, JS, images, and other static files"""
    return send_from_directory('.', filename)

@app.route('/analyze', methods=['POST', 'OPTIONS'])
def analyze_image():
    """
    Main endpoint: Analyze uploaded crop image for diseases
    Expects: image file in POST request
    Returns: JSON with disease analysis
    """
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'preflight OK'})
        response.headers.add('Access-Control-Allow-Origin', 'https://krishi-mitra-crob.onrender.com')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response, 200
        
    try:
        # Check if image was uploaded
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file type
        if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            return jsonify({'error': 'Invalid file type. Please upload JPG, JPEG, or PNG image'}), 400
        
        logger.info(f"📸 Analyzing image: {file.filename}")
        
        # Read the image
        image_data = file.read()
        
        if len(image_data) == 0:
            return jsonify({'error': 'Empty file uploaded'}), 400
            
        # Check file size (max 10MB)
        if len(image_data) > 10 * 1024 * 1024:
            return jsonify({'error': 'File too large. Maximum size is 10MB'}), 400
            
        image = Image.open(io.BytesIO(image_data))
        
        # Check image size
        if image.size[0] < 50 or image.size[1] < 50:
            return jsonify({'error': 'Image too small. Please upload a larger image (min 50x50 pixels).'}), 400
        
        # Check if model is available
        if model is None:
            logger.warning("Model not available, using demo response")
            # Return demo response instead of error
            demo_result = {
                'disease': 'healthy',
                'confidence': 0.85,
                'detailed_class': 'Tomato___healthy',
                'note': 'Demo mode - model not loaded'
            }
            return jsonify(demo_result)
        
        # Get AI prediction
        result = model.predict(image)
        
        logger.info(f"✅ Analysis complete: {result['disease']} ({result.get('confidence', 0):.1%} confidence)")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Analysis error: {str(e)}")
        # Return demo response instead of error for better UX
        demo_result = {
            'disease': 'healthy',
            'confidence': 0.75,
            'detailed_class': 'Tomato___healthy', 
            'note': f'Demo mode - analysis error: {str(e)}'
        }
        return jsonify(demo_result)

@app.route('/health', methods=['GET', 'OPTIONS'])
def health_check():
    """Health check endpoint for monitoring"""
    if request.method == 'OPTIONS':
        return '', 200
        
    model_status = 'healthy' if model is not None else 'unavailable'
    model_loaded = model.model is not None if model else False
    
    return jsonify({
        'status': 'healthy',
        'service': 'krishi_mitra_api',
        'model_status': model_status,
        'model_loaded': model_loaded,
        'deployment': 'render',
        'supported_diseases': len(model.classes) if model else 0,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/classes', methods=['GET'])
def list_classes():
    """List all supported disease classes"""
    if model is None:
        return jsonify({
            'classes': ['Tomato___healthy', 'Tomato___Early_blight', 'Tomato___Late_blight', 'Tomato___Bacterial_spot'],
            'simple_mapping': {
                'Tomato___healthy': 'healthy',
                'Tomato___Early_blight': 'leaf_spot_early', 
                'Tomato___Late_blight': 'leaf_spot_late',
                'Tomato___Bacterial_spot': 'bacterial_blight'
            },
            'total_classes': 4,
            'note': 'Demo mode - model not loaded'
        })
        
    return jsonify({
        'classes': model.classes,
        'simple_mapping': model.plantvillage_to_simple,
        'total_classes': len(model.classes)
    })

@app.route('/test', methods=['GET'])
def test_endpoint():
    """Simple test endpoint to verify server is running"""
    return jsonify({
        'message': 'Krishi Mitra API is running!',
        'timestamp': datetime.now().isoformat(),
        'status': 'operational',
        'cors_enabled': True
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 Error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(413)
def too_large(error):
    return jsonify({'error': 'File too large'}), 413

# Startup message
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    
    print("\n" + "="*60)
    print("🌱 Krishi Mitra - Crop Disease Detection API")
    print("="*60)
    print(f"🤖 AI Model: {'TRAINED MODEL ✅' if model and model.model else 'DEMO MODE 🔮'}")
    print(f"🎯 Supported Diseases: {len(model.classes) if model else 4}")
    print(f"🌐 Server: http://0.0.0.0:{port}")
    print(f"🚀 Environment: {'PRODUCTION' if port != 5000 else 'DEVELOPMENT'}")
    print(f"🔧 CORS Enabled: True")
    print(f"📍 Allowed Origins: https://krishi-mitra-crob.onrender.com")
    print("="*60)
    print("💡 Endpoints:")
    print("   GET  /          - Frontend interface")
    print("   POST /analyze   - Analyze crop image")
    print("   GET  /health    - Health check")
    print("   GET  /classes   - List diseases")
    print("   GET  /test      - Simple test")
    print("="*60)
    
    # Start the server
    app.run(host='0.0.0.0', port=port, debug=False)
