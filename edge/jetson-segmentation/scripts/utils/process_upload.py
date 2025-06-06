import os
import sys
import hashlib
import zipfile
from pathlib import Path
from cryptography.fernet import Fernet
from typing import Optional

def verify_checksum(file_path: str, expected_checksum: Optional[str] = None) -> bool:
    """Verify file integrity using SHA-256."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    actual_checksum = sha256_hash.hexdigest()
    
    if expected_checksum:
        return actual_checksum == expected_checksum
    return actual_checksum

def decrypt_file(input_path: str, output_path: str, key: str) -> bool:
    """Decrypt an encrypted file using Fernet."""
    try:
        f = Fernet(key.encode())
        with open(input_path, 'rb') as encrypted_file:
            encrypted_data = encrypted_file.read()
        decrypted_data = f.decrypt(encrypted_data)
        with open(output_path, 'wb') as decrypted_file:
            decrypted_file.write(decrypted_data)
        return True
    except Exception as e:
        print(f"Decryption error: {e}")
        return False

def process_upload(input_path: str, output_dir: str, encryption_key: Optional[str] = None) -> bool:
    """Process uploaded file (zip or encrypted) and extract images."""
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        if encryption_key:
            temp_path = input_path + '.dec'
            if not decrypt_file(input_path, temp_path, encryption_key):
                return False
            input_path = temp_path
        
        with zipfile.ZipFile(input_path, 'r') as zip_ref:
            for file in zip_ref.namelist():
                if file.startswith(('/', '..')) or '..' in file:
                    raise ValueError(f"Invalid path in zip: {file}")
                
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.tif')):
                    zip_ref.extract(file, output_dir)
        
        if encryption_key and os.path.exists(temp_path):
            os.remove(temp_path)
        
        return True
    except Exception as e:
        print(f"Processing error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: process_upload.py <input_file> <output_dir> [encryption_key]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    key = sys.argv[3] if len(sys.argv) > 3 else None
    
    if process_upload(input_file, output_dir, key):
        print("Upload processed successfully")
        sys.exit(0)
    else:
        print("Upload processing failed")
        sys.exit(1)
