"""
download_model.py

Download a large model file from Google Drive using gdown.

Usage:
    - Set the environment variable GOOGLE_DRIVE_ID to your file id (the long id found in the share URL).
    - Optionally set MODEL_OUTPUT_PATH (default: crop_disease_model.h5)
    - Run: python download_model.py

This script does a streaming download and will overwrite an existing file only if --force is used.
"""

import os
import sys
import time
import gdown

DEFAULT_OUTPUT = os.environ.get('MODEL_OUTPUT_PATH', 'crop_disease_model.h5')
DRIVE_ID = os.environ.get('GOOGLE_DRIVE_ID')
FORCE = os.environ.get('FORCE_MODEL_DOWNLOAD', 'false').lower() in ('1', 'true', 'yes')

def download_from_gdrive(file_id: str, output_path: str):
    url = f'https://drive.google.com/uc?id={file_id}'
    print(f"➡️ Downloading model from Google Drive id={file_id} -> {output_path}")
    # gdown supports resumable downloads and large files
    try:
        gdown.download(url, output_path, quiet=False, fuzzy=True, use_cookies=False)
    except Exception as e:
        print("❌ gdown failed:", e)
        raise

if __name__ == '__main__':
    if not DRIVE_ID:
        print("❌ GOOGLE_DRIVE_ID environment variable not set. Aborting.")
        sys.exit(2)

    target = DEFAULT_OUTPUT
    if os.path.exists(target) and not FORCE:
        print(f"ℹ️ Model already exists at {target}. Use FORCE_MODEL_DOWNLOAD=1 to overwrite.")
        sys.exit(0)

    try:
        download_from_gdrive(DRIVE_ID, target)
        print("✅ Model download likely complete. Verifying file exists...")
        if os.path.exists(target):
            print(f"✅ File present: {target} (size: {os.path.getsize(target)} bytes)")
            sys.exit(0)
        else:
            print("❌ Download finished but file not found. Please check Google Drive sharing settings.")
            sys.exit(3)
    except Exception as ex:
        print("❌ Download failed:", ex)
        sys.exit(4)