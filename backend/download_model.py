import gdown
import os

def download_model():
    model_path = 'crop_disease_model.h5'
    
    if not os.path.exists(model_path):
        print("Downloading trained model...")
        
        # Replace with YOUR actual Google Drive file ID
        file_id = "1p7pJXsRjaXZLGO1-ZRFbdiG2OpP-sY8b"
        url = f"https://drive.google.com/uc?id=1p7pJXsRjaXZLGO1-ZRFbdiG2OpP-sY8b&export=download"
        
        gdown.download(url, model_path, quiet=False)
        print("Model downloaded successfully!")
    else:
        print("Model already exists!")

if __name__ == "__main__":
    download_model()
