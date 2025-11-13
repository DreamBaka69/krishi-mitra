import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import logging
import io
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Configure CORS - SIMPLIFIED (allow all for testing)
CORS(app)  # This allows all origins - we can restrict later

# Global model variable
model = None

logger.info("🌱 Krishi Mitra Backend Starting...")

@app.route('/')
def home():
    """Serve the main frontend page"""
    try:
        return send_from_directory('.', 'index.html')
    except:
        return jsonify({"message": "🌱 Krishi Mitra Backend API", "status": "running"})

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('.', filename)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'krishi_mitra_backend',
        'model_loaded': model is not None,
        'timestamp': datetime.now().isoformat(),
        'version': '1.0'
    })

@app.route('/test', methods=['GET'])
def test_endpoint():
    """Test endpoint"""
    return jsonify({
        'message': '✅ Backend is working!',
        'endpoint': '/test',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/analyze', methods=['POST', 'OPTIONS'])
def analyze_image():
    """Analyze crop image for diseases"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'preflight OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response

    try:
        logger.info("📨 Received analyze request")
        
        # Check if image was uploaded
        if 'image' not in request.files:
            logger.error("❌ No image in request.files")
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        logger.info(f"📸 File received: {file.filename}")
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file type
        if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            return jsonify({'error': 'Invalid file type. Please upload JPG, JPEG, or PNG'}), 400
        
        # Read and validate image
        image_data = file.read()
        logger.info(f"📊 Image size: {len(image_data)} bytes")
        
        if len(image_data) == 0:
            return jsonify({'error': 'Empty file uploaded'}), 400
            
        # Check file size (max 10MB)
        if len(image_data) > 10 * 1024 * 1024:
            return jsonify({'error': 'File too large. Maximum size is 10MB'}), 400
            
        # Try to open image
        try:
            image = Image.open(io.BytesIO(image_data))
            logger.info(f"🖼️ Image opened: {image.size} - {image.format}")
        except Exception as e:
            logger.error(f"❌ Image open error: {str(e)}")
            return jsonify({'error': f'Invalid image file: {str(e)}'}), 400
        
        # Check image dimensions
        if image.size[0] < 50 or image.size[1] < 50:
            return jsonify({'error': 'Image too small. Minimum size is 50x50 pixels.'}), 400
        
        # SUCCESS: Return analysis result
        demo_result = {
            'disease': 'healthy',
            'confidence': 0.89,
            'detailed_class': 'Tomato___healthy',
            'image_size': f"{image.size[0]}x{image.size[1]}",
            'format': image.format,
            'note': 'Demo analysis - AI model integration pending',
            'success': True
        }
        
        logger.info(f"✅ Analysis complete: {demo_result['disease']}")
        
        response = jsonify(demo_result)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        logger.error(f"❌ Analysis error: {str(e)}")
        return jsonify({
            'error': f'Analysis failed: {str(e)}',
            'disease': 'healthy',
            'confidence': 0.75,
            'detailed_class': 'Tomato___healthy',
            'note': 'Fallback due to error',
            'success': False
        }), 500

@app.route('/classes', methods=['GET'])
def list_classes():
    """List supported disease classes"""
    classes = [
        'Tomato___healthy',
        'Tomato___Early_blight', 
        'Tomato___Late_blight',
        'Tomato___Bacterial_spot'
    ]
    
    simple_mapping = {
        'Tomato___healthy': 'healthy',
        'Tomato___Early_blight': 'leaf_spot_early',
        'Tomato___Late_blight': 'leaf_spot_late', 
        'Tomato___Bacterial_spot': 'bacterial_blight'
    }
    
    return jsonify({
        'classes': classes,
        'simple_mapping': simple_mapping,
        'total_classes': len(classes),
        'note': 'Demo classes - update with actual model classes'
    })

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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    
    print("\n" + "="*60)
    print("🌱 Krishi Mitra - Crop Disease Detection API")
    print("="*60)
    print(f"🚀 Server: http://0.0.0.0:{port}")
    print(f"🔧 CORS: Enabled for all origins")
    print("="*60)
    print("💡 Endpoints:")
    print("   GET  /          - Frontend interface")
    print("   POST /analyze   - Analyze crop image") 
    print("   GET  /health    - Health check")
    print("   GET  /classes   - List diseases")
    print("   GET  /test      - Simple test")
    print("="*60)
    
    app.run(host='0.0.0.0', port=port, debug=False)
