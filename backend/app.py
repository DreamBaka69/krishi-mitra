from flask import Flask, jsonify
from flask_cors import CORS

print("🚀 STARTING FLASK APP...")

app = Flask(__name__)
CORS(app)

print("✅ FLASK APP CREATED")

@app.route('/')
def home():
    print("📍 Home route called")
    return jsonify({"message": "Root route working!", "status": "success"})

@app.route('/health')
def health_check():
    print("📍 Health route called") 
    return jsonify({"status": "healthy", "message": "Health check working"})

@app.route('/test')
def test_route():
    print("📍 Test route called")
    return jsonify({"message": "Test route working!"})

@app.route('/analyze', methods=['POST', 'GET'])
def analyze_route():
    print("📍 Analyze route called")
    return jsonify({"disease": "healthy", "confidence": 0.95, "message": "Analyze route working"})

@app.route('/debug')
def debug_route():
    print("📍 Debug route called")
    return jsonify({
        "routes": ["/", "/health", "/test", "/analyze", "/debug"],
        "status": "all_routes_working"
    })

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 10000))
    
    print("🔧 REGISTERED ROUTES:")
    for rule in app.url_map.iter_rules():
        print(f"   {rule.rule} -> {rule.endpoint}")
    
    print(f"🌐 STARTING SERVER ON PORT {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
