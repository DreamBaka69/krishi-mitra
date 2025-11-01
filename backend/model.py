import tensorflow as tf
import numpy as np
from PIL import Image
import os
import logging

logger = logging.getLogger('krishi_mitra')

class CropDiseaseModel:
    """
    AI model for detecting crop diseases from images.
    This works with the PlantVillage dataset.
    """
    
    def __init__(self, model_path=None):
        # Map PlantVillage names to simple names for frontend
        self.plantvillage_to_simple = {
            'Tomato___healthy': 'healthy',
            'Tomato___Bacterial_spot': 'bacterial_blight', 
            'Tomato___Early_blight': 'leaf_spot_early',
            'Tomato___Late_blight': 'leaf_spot_late'
        }
        
        # Load available classes
        self.classes = self.load_class_names()
        self.model = self.load_model(model_path)
        
        logger.info(f"🤖 AI Model Ready! Classes: {list(self.plantvillage_to_simple.keys())}")
    
    def load_class_names(self):
        """Load class names from file or use defaults"""
        try:
            if os.path.exists('class_names.txt'):
                with open('class_names.txt', 'r') as f:
                    return [line.strip() for line in f.readlines()]
            else:
                logger.warning("class_names.txt not found, using default classes")
                return list(self.plantvillage_to_simple.keys())
        except Exception as e:
            logger.error(f"Error loading class names: {e}")
            return list(self.plantvillage_to_simple.keys())
    
    def load_model(self, model_path):
        """Load the trained model file"""
        if model_path and os.path.exists(model_path):
            try:
                logger.info(f"📦 Loading trained model from {model_path}...")
                model = tf.keras.models.load_model(model_path)
                logger.info("✅ Model loaded successfully!")
                return model
            except Exception as e:
                logger.error(f"❌ Error loading model: {e}")
                logger.info("🔮 Using mock mode for demo")
                return None
        else:
            logger.info("🔮 No model file found. Using mock mode for demo.")
            return None
    
    def preprocess_image(self, image):
        """Prepare image for the AI model"""
        try:
            # Resize to what the model expects
            image = image.resize((128, 128))
            img_array = np.array(image) / 255.0  # Normalize pixels
            
            # Make sure image has 3 color channels (RGB)
            if len(img_array.shape) == 2:  # Grayscale
                img_array = np.stack([img_array]*3, axis=-1)
            elif img_array.shape[2] == 4:  # RGBA (has transparency)
                img_array = img_array[:,:,:3]  # Remove alpha channel
            
            return np.expand_dims(img_array, axis=0)  # Add batch dimension
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            raise
    
    def predict(self, image):
        """
        Analyze image and detect disease
        Returns: {'disease': 'healthy', 'confidence': 0.95, ...}
        """
        try:
            if self.model:
                # Real AI prediction
                processed_img = self.preprocess_image(image)
                prediction = self.model.predict(processed_img, verbose=0)
                predicted_class_idx = np.argmax(prediction[0])
                confidence = prediction[0][predicted_class_idx]
                
                # Get the PlantVillage class name
                plantvillage_name = self.classes[predicted_class_idx]
            else:
                # Mock prediction for demo (when no trained model)
                predicted_class_idx = np.random.randint(0, len(self.classes))
                confidence = 0.7 + np.random.random() * 0.25
                plantvillage_name = self.classes[predicted_class_idx]
            
            # Convert to simple name for frontend
            simple_name = self.plantvillage_to_simple.get(plantvillage_name, 'healthy')
            
            logger.info(f"Prediction: {simple_name} ({confidence:.2%})")
            
            return {
                'disease': simple_name,
                'confidence': float(confidence),
                'detailed_class': plantvillage_name,
                'model_used': 'real' if self.model else 'mock'
            }
            
        except Exception as e:
            logger.error(f"❌ Prediction error: {e}")
            # Return safe result if something goes wrong
            return {
                'disease': 'healthy',
                'confidence': 0.5,
                'detailed_class': 'Tomato___healthy',
                'model_used': 'error',
                'error': str(e)
            }