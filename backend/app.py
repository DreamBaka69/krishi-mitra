from flask import Flask, jsonify
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

@app.route('/')
def home():
    return jsonify({"message": "🌱 Krishi Mitra Backend is LIVE!"})

@app.route('/health')
def health():
    logger.info("Health check called")
    return jsonify({
        "status": "healthy",
        "service": "krishi_mitra_backend", 
        "timestamp": datetime.now().isoformat(),
        "environment": "production"
    })

@app.route('/test')
def test():
    return jsonify({
        "message": "✅ Backend is working!",
        "endpoint": "/test",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/classes')
def classes():
    return jsonify({
        "classes": ["Tomato___healthy", "Tomato___Early_blight", "Tomato___Late_blight"],
        "total": 3,
        "status": "demo"
    })

@app.route('/analyze', methods=['POST', 'OPTIONS'])
def analyze():
    # Always return a successful demo response
    return jsonify({
        "disease": "healthy",
        "confidence": 0.92,
        "detailed_class": "Tomato___healthy",
        "note": "Demo analysis - backend operational"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🚀 Starting Krishi Mitra backend on port {port}")
    print(f"✅ Flask app starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
