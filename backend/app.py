from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Debug all requests
@app.before_request
def log_request_info():
    logger.info(f"📨 Incoming request: {request.method} {request.path}")

@app.route('/')
def home():
    logger.info("✅ Home route executed")
    return jsonify({"message": "🌱 Root route working!", "status": "success"})

@app.route('/health')
def health():
    logger.info("✅ Health route executed")
    return jsonify({"status": "healthy", "route": "/health"})

@app.route('/test')
def test():
    logger.info("✅ Test route executed") 
    return jsonify({"message": "Test route working!", "route": "/test"})

@app.route('/analyze', methods=['POST', 'GET', 'OPTIONS'])
def analyze():
    logger.info("✅ Analyze route executed")
    if request.method == 'GET':
        return jsonify({"message": "Analyze route working! Use POST for analysis.", "route": "/analyze"})
    return jsonify({"disease": "healthy", "confidence": 0.95, "message": "Demo analysis"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🚀 Starting server on port {port}")
    logger.info(f"📍 Registered routes: {[rule.rule for rule in app.url_map.iter_rules()]}")
    app.run(host='0.0.0.0', port=port, debug=False)
