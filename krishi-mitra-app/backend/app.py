import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from model import CropDiseaseModel
from PIL import Image
import io
import disease_info
import subprocess
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ENV-configurable model filename/path
# Default file name expected: crop_disease_model.h5 in same folder
MODEL_ENV_PATH = os.environ.get('MODEL_PATH', 'crop_disease_model.h5')
MODEL_PATH = MODEL_ENV_PATH if os.path.isabs(MODEL_ENV_PATH) else os.path.join(BASE_DIR, MODEL_ENV_PATH)

# Google Drive ID (optional) for automatic download if model not present
GOOGLE_DRIVE_ID = os.environ.get('GOOGLE_DRIVE_ID')
MODEL_OUTPUT_PATH = os.environ.get('MODEL_OUTPUT_PATH', MODEL_PATH)

print("🌱 Starting Krishi Mitra Server...")

# If model file is missing and GOOGLE_DRIVE_ID is set, attempt to download synchronously
if not os.path.exists(MODEL_PATH) and GOOGLE_DRIVE_ID:
    print(f"📥 Model not found at {MODEL_PATH}. GOOGLE_DRIVE_ID detected; attempting download...")
    # Call download_model.py in-process via subprocess so we rely on same environment
    download_script = os.path.join(BASE_DIR, 'download_model.py')
    if os.path.exists(download_script):
        try:
            env = os.environ.copy()
            env['GOOGLE_DRIVE_ID'] = GOOGLE_DRIVE_ID
            env['MODEL_OUTPUT_PATH'] = MODEL_OUTPUT_PATH
            # Run script and stream output
            rc = subprocess.call([sys.executable, download_script], env=env)
            if rc == 0:
                print("✅ Model downloaded successfully.")
            else:
                print(f"⚠️ download_model.py exited with code {rc}; continuing without model (demo mode).")
        except Exception as e:
            print(f"❌ Failed to run download_model.py: {e}")
    else:
        print("❌ download_model.py not found. Cannot auto-download model.")
else:
    if os.path.exists(MODEL_PATH):
        print(f"📦 Model file found at {MODEL_PATH}")
    else:
        print("⚠️ No GOOGLE_DRIVE_ID provided and model file missing — fallback demo mode will be used.")

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Allow frontend to connect

# Initialize AI model (CropDiseaseModel handles None model gracefully)
try:
    model = CropDiseaseModel(MODEL_PATH)
except Exception as e:
    print("❌ Failed to initialize model object:", e)
    model = CropDiseaseModel(None)

@app.route('/')
def home():
    return jsonify({
        'message': '🌱 Krishi Mitra - AI Crop Disease Detection',
        'status': 'active',
        'endpoints': {
            '/': 'Get this info',
            '/analyze': 'POST - Analyze crop image (file form field "image")',
            '/health': 'Check server status',
            '/classes': 'List supported diseases and mappings (grouped by crop)'
        }
    })

@app.route('/analyze', methods=['POST'])
def analyze_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            return jsonify({'error': 'Please upload JPG or PNG image'}), 400
        
        print(f"📸 Analyzing: {file.filename}")
        image_data = file.read()
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
        if image.size[0] < 50 or image.size[1] < 50:
            return jsonify({'error': 'Image too small. Please upload a larger image.'}), 400
        
        result = model.predict(image)
        simple_slug = result.get('disease')
        info = disease_info.get_info_for_simple(simple_slug)
        
        payload = {
            'plant': result.get('plant'),
            'disease': simple_slug,
            'confidence': result.get('confidence'),
            'detailed_class': result.get('detailed_class'),
            'model_used': result.get('model_used'),
            'advice': {
                'friendly_name': info['friendly_name'],
                'treatment': info['treatment'],
                'prevention': info['prevention'],
                'example_classes': info.get('example_classes', [])
            }
        }
        
        print(f"✅ Result: {payload['plant']} - {payload['disease']} ({payload['confidence']:.1%} confidence)")
        return jsonify(payload)
        
    except Exception as e:
        print(f"❌ Server error: {e}")
        return jsonify({'error': 'Server error. Please try again.'}), 500

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'model_loaded': model.model is not None,
        'supported_diseases': len(model.classes)
    })

@app.route('/classes')
def list_classes():
    advice_map = {}
    for simple_slug, pv_list in model.simple_to_plantvillage.items():
        info = disease_info.get_info_for_simple(simple_slug)
        advice_map[simple_slug] = {
            'friendly_name': info['friendly_name'],
            'treatment': info['treatment'],
            'prevention': info['prevention'],
            'example_classes': info.get('example_classes', pv_list)
        }

    return jsonify({
        'classes': model.classes,
        'plantvillage_to_simple': model.plantvillage_to_simple,
        'simple_to_plantvillage': model.simple_to_plantvillage,
        'by_plant': model.classes_by_plant,
        'disease_info': advice_map
    })

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🌱 Krishi Mitra - Crop Disease Detection (local debug)")
    print("="*50)
    print(f"🤖 AI Model: {'TRAINED MODEL' if model.model else 'DEMO MODE'}")
    print(f"🎯 Can detect: {len(model.classes)} diseases")
    print("🌐 Server: http://localhost:5000")
    print("="*50)
    app.run(debug=True, host='0.0.0.0', port=5000)