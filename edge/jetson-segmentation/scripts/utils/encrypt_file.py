import sys
import hashlib
from pathlib import Path
from cryptography.fernet import Fernet
from typing import Tuple

def encrypt_file(input_path: str, output_path: str, key: str) -> Tuple[bool, str]:
    """Encrypt a file using Fernet symmetric encryption."""
    try:
        f = Fernet(key.encode())
        
        with open(input_path, 'rb') as file:
            data = file.read()
        encrypted_data = f.encrypt(data)
        
        with open(output_path, 'wb') as file:
            file.write(encrypted_data)
        
        sha256_hash = hashlib.sha256()
        sha256_hash.update(encrypted_data)
        checksum = sha256_hash.hexdigest()
        
        return True, checksum
    except Exception as e:
        print(f"Encryption error: {e}")
        return False, ""

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: encrypt_file.py <input_file> <output_file> <encryption_key>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    key = sys.argv[3]
    
    if not Path(input_file).is_file():
        print(f"Input file not found: {input_file}")
        sys.exit(1)
    
    success, checksum = encrypt_file(input_file, output_file, key)
    
    if success:
        print(f"File encrypted successfully!")
        print(f"Encrypted file: {output_file}")
        print(f"SHA-256 checksum: {checksum}")
        print("\nUse this checksum when running the GitHub Action for verification.")
    else:
        print("Encryption failed!")
        sys.exit(1)
