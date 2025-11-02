import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from model import CropDiseaseModel
from PIL import Image
import io
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('krishi_mitra')

# Create Flask app
app = Flask(__name__)

# Configure CORS for production
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://krish-mitra-crob.onrender.com",  
            "https://DreamBaka69.github.io/Krishi-mitra/",
            "http://localhost:3000",
            "http://127.0.0.1:3000", 
            "http://localhost:5000",
            "http://127.0.0.1:5000"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
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

@app.route('/')
def home():
    """Welcome message and API information"""
    return jsonify({
        'message': '🌱 Krishi Mitra - AI Crop Disease Detection API',
        'status': 'active',
        'version': '1.0.0',
        'model_status': 'loaded' if model and model.model else 'demo_mode',
        'deployment': 'render_production',
        'endpoints': {
            '/': 'GET - API information',
            '/analyze': 'POST - Analyze crop image for diseases',
            '/health': 'GET - Health check',
            '/classes': 'GET - List supported disease classes'
        },
        'usage': 'Send POST request to /analyze with image file'
    })

@app.route('/analyze', methods=['POST', 'OPTIONS'])
def analyze_image():
    """
    Main endpoint: Analyze uploaded crop image for diseases
    Expects: image file in POST request
    Returns: JSON with disease analysis
    """
    if request.method == 'OPTIONS':
        return '', 200
        
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
            return jsonify({'error': 'AI model not available. Please try again later.'}), 500
        
        # Get AI prediction
        result = model.predict(image)
        
        logger.info(f"✅ Analysis complete: {result['disease']} ({result.get('confidence', 0):.1%} confidence)")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Analysis error: {str(e)}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    model_status = 'healthy' if model is not None else 'unavailable'
    model_loaded = model.model is not None if model else False
    
    return jsonify({
        'status': 'healthy',
        'service': 'krishi_mitra_api',
        'model_status': model_status,
        'model_loaded': model_loaded,
        'deployment': 'render',
        'supported_diseases': len(model.classes) if model else 0,
        'timestamp': __import__('datetime').datetime.now().isoformat()
    })

@app.route('/classes', methods=['GET'])
def list_classes():
    """List all supported disease classes"""
    if model is None:
        return jsonify({'error': 'Model not available'}), 500
        
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
        'timestamp': __import__('datetime').datetime.now().isoformat(),
        'status': 'operational'
    })

# Serve frontend files
@app.route('/')
def serve_frontend():
    """Serve the main frontend page"""
    try:
        # Try multiple possible locations for frontend files
        frontend_paths = [
            './frontend',
            '../frontend', 
            './../frontend',
            'frontend'
        ]
        
        for frontend_path in frontend_paths:
            try:
                return send_from_directory(frontend_path, 'index.html')
            except:
                continue
                
        # If frontend not found, show API info
        logger.warning("Frontend files not found, serving API info")
        return jsonify({
            'message': '🌱 Krishi Mitra - AI Crop Disease Detection API',
            'status': 'active',
            'version': '1.0.0',
            'model_status': 'demo_mode',
            'note': 'Frontend not deployed - use API endpoints directly',
            'endpoints': {
                '/analyze': 'POST - Analyze crop image for diseases',
                '/health': 'GET - Health check',
                '/classes': 'GET - List supported disease classes'
            },
            'usage': 'Send POST request to /analyze with image file'
        })
        
    except Exception as e:
        logger.error(f"Frontend serving error: {e}")
        return jsonify({'error': 'Frontend not available', 'api_status': 'active'})

@app.route('/<path:path>')
def serve_static_files(path):
    """Serve static files (CSS, JS, images) for the frontend"""
    frontend_paths = ['./frontend', '../frontend', './../frontend', 'frontend']
    
    for frontend_path in frontend_paths:
        try:
            return send_from_directory(frontend_path, path)
        except:
            continue
            
    return jsonify({'error': 'File not found'}), 404

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
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
    print(f"🎯 Supported Diseases: {len(model.classes) if model else 0}")
    print(f"🌐 Server: http://0.0.0.0:{port}")
    print(f"🚀 Environment: {'PRODUCTION' if port != 5000 else 'DEVELOPMENT'}")
    print("="*60)
    print("💡 Endpoints:")
    print("   GET  /          - API information")
    print("   POST /analyze   - Analyze crop image")
    print("   GET  /health    - Health check")
    print("   GET  /classes   - List diseases")
    print("   GET  /test      - Simple test")
    print("="*60)
    
    # Start the server

    app.run(host='0.0.0.0', port=port, debug=False)


