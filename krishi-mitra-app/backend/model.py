"""
model.py

CropDiseaseModel:
- Loads a Keras model (HDF5 or SavedModel) if MODEL_PATH is provided and exists.
- Loads class names from class_names.txt (one class name per line).
- Builds helpful mappings:
    - classes: list of full class labels (as in class_names.txt)
    - classes_by_plant: dict mapping plant -> [classes...]
    - plantvillage_to_simple, simple_to_plantvillage (best-effort)
- predict(image: PIL.Image.Image) -> dict:
    - Preprocesses to model input shape, runs model.predict if available.
    - If model missing, returns a deterministic demo response (first class).
- Robust to missing files and works in demo mode.

Expected files:
- class_names.txt (one class per line, e.g., "Tomato___Healthy" or "Tomato___Late_blight")
- crop_disease_model.h5  (or other model file at path you pass)
"""

import os
import numpy as np
from PIL import Image
import traceback

try:
    import tensorflow as tf
    load_model = tf.keras.models.load_model
    TF_AVAILABLE = True
except Exception:
    TF_AVAILABLE = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEFAULT_CLASS_NAMES = os.path.join(BASE_DIR, "class_names.txt")

def safe_readlines(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [ln.strip() for ln in f if ln.strip()]
    except Exception:
        return []

class CropDiseaseModel:
    def __init__(self, model_path=None, class_names_path=None, input_size=(224,224)):
        """
        model_path: path to keras model file (h5 or saved model). If None or missing, operates in demo mode.
        class_names_path: path to class_names.txt
        input_size: (width, height) expected by the model
        """
        self.base_dir = BASE_DIR
        self.input_size = tuple(input_size)
        self.model_path = model_path
        self.class_names_path = class_names_path or DEFAULT_CLASS_NAMES

        # Load class names
        self.classes = safe_readlines(self.class_names_path)
        if not self.classes:
            # Provide fallback demo classes if file missing
            self.classes = [
                "Tomato___Late_blight",
                "Tomato___Healthy",
                "Potato___Early_blight",
                "Potato___Healthy",
                "Corn___Common_rust",
                "Corn___Healthy"
            ]

        # Build some mappings
        self.classes_by_plant = {}
        for c in self.classes:
            # Expect format "Plant___Disease" or "Plant - Disease" fallback
            if "___" in c:
                plant = c.split("___", 1)[0]
            elif " - " in c:
                plant = c.split(" - ", 1)[0]
            else:
                # fallback: plant name from first token before underscore
                plant = c.split("_")[0]
            self.classes_by_plant.setdefault(plant, []).append(c)

        # plantvillage <-> simple slug mapping (simple slug: lowercase plant_disease)
        self.plantvillage_to_simple = {}
        self.simple_to_plantvillage = {}
        for full in self.classes:
            simple = full.replace("___", "_").replace(" ", "_").lower()
            self.plantvillage_to_simple[full] = simple
            self.simple_to_plantvillage[simple] = full

        # Attempt to load the model if model_path exists and TF available
        self.model = None
        self.model_input_shape = (self.input_size[0], self.input_size[1], 3)
        if model_path and os.path.exists(model_path) and TF_AVAILABLE:
            try:
                # load_model will handle saved_model dirs and h5 files
                print(f"[model.py] Loading model from: {model_path}")
                # allow custom objects if needed later
                self.model = load_model(model_path, compile=False)
                # try to infer input size from model if possible
                try:
                    mshape = self.model.input_shape
                    # mshape often is (None, h, w, c) or (None, c, h, w)
                    if isinstance(mshape, tuple) and len(mshape) >= 3:
                        if mshape[1] is None:
                            # fallback
                            pass
                        else:
                            # If channels-last
                            if len(mshape) == 4:
                                h, w = mshape[1], mshape[2]
                                self.input_size = (w, h)
                                self.model_input_shape = (h, w, mshape[3] if len(mshape) == 4 else 3)
                except Exception:
                    pass
                print(f"[model.py] Model loaded. Input size: {self.input_size}")
            except Exception as e:
                print("[model.py] Failed to load model:", e)
                traceback.print_exc()
                self.model = None
        else:
            if model_path:
                print(f"[model.py] Model path provided but missing or TF not available: {model_path}")
            else:
                print("[model.py] No model path provided. Running in demo fallback mode.")

        # Determine final list of simple slugs (same order as classes)
        self.simple_classes = [self.plantvillage_to_simple.get(c, c.replace(" ", "_").lower()) for c in self.classes]

        # helper: mapping from index -> class
        self.index_to_class = {i: c for i, c in enumerate(self.classes)}

    def preprocess(self, image):
        """
        Accepts a PIL.Image (RGB) and returns numpy array shaped (1, H, W, 3), floats scaled 0..1
        """
        # Ensure RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')
        # Resize maintaining aspect ratio but fit in input size by padding center
        target_w, target_h = self.input_size
        image = image.resize((target_w, target_h), Image.LANCZOS)
        arr = np.asarray(image).astype('float32') / 255.0
        # Ensure shape
        if arr.ndim == 2:
            arr = np.stack([arr]*3, axis=-1)
        if arr.shape[2] == 4:
            arr = arr[..., :3]
        arr = np.expand_dims(arr, axis=0)
        return arr

    def softmax(self, x):
        e = np.exp(x - np.max(x))
        return e / e.sum(axis=-1, keepdims=True)

    def predict(self, image_pil):
        """
        image_pil: PIL Image object (RGB)
        Returns dict with keys:
            - plant (string)
            - disease (simple slug)
            - confidence (float 0..1)
            - detailed_class (Plant___Disease)
            - model_used (string: path or 'demo')
        """
        try:
            x = self.preprocess(image_pil)
            if self.model is not None:
                # Model should return logits or probabilities
                preds = self.model.predict(x, verbose=0)
                preds = np.asarray(preds).reshape(-1)
                # Try to interpret as logits if sums not 1
                if not np.allclose(preds.sum(), 1.0, atol=1e-3):
                    probs = self.softmax(preds)
                else:
                    probs = preds
                idx = int(np.argmax(probs))
                confidence = float(probs[idx])
                detailed = self.index_to_class.get(idx, "Unknown")
                simple = self.plantvillage_to_simple.get(detailed, detailed.replace(" ", "_").lower())
                plant = detailed.split("___", 1)[0] if "___" in detailed else detailed.split("_")[0]
                return {
                    'plant': plant,
                    'disease': simple,
                    'confidence': confidence,
                    'detailed_class': detailed,
                    'model_used': os.path.basename(self.model_path) if self.model_path else 'trained-model'
                }
            else:
                # Demo mode: pick deterministic class based on image content hash
                # Simple deterministic fallback: average pixel value -> index
                avg = np.mean(x)
                idx = int(min(len(self.classes)-1, max(0, int(avg * len(self.classes)))))
                detailed = self.index_to_class.get(idx, self.classes[0])
                simple = self.plantvillage_to_simple.get(detailed, detailed.replace(" ", "_").lower())
                plant = detailed.split("___", 1)[0] if "___" in detailed else detailed.split("_")[0]
                confidence = 0.5 + (avg % 0.5)  # pseudo-confidence
                return {
                    'plant': plant,
                    'disease': simple,
                    'confidence': float(confidence),
                    'detailed_class': detailed,
                    'model_used': 'demo-mode'
                }
        except Exception as e:
            print("[model.py] Error during prediction:", e)
            traceback.print_exc()
            # Return safe fallback
            fallback = self.classes[0]
            simple = self.plantvillage_to_simple.get(fallback, fallback.replace(" ", "_").lower())
            plant = fallback.split("___", 1)[0] if "___" in fallback else fallback.split("_")[0]
            return {
                'plant': plant,
                'disease': simple,
                'confidence': 0.0,
                'detailed_class': fallback,
                'model_used': 'error'
            }