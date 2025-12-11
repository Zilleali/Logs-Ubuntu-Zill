#!/usr/bin/env python3
"""
Data encryption for sensitive logs
"""

from cryptography.fernet import Fernet
import base64
import os

class LogEncryptor:
    def __init__(self, key_file="~/.logs_encryption.key"):
        self.key_file = os.path.expanduser(key_file)
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)
    
    def _get_or_create_key(self):
        """Get existing key or create new one"""
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            os.chmod(self.key_file, 0o600)  # Secure permissions
            return key
    
    def encrypt(self, data):
        """Encrypt data"""
        if isinstance(data, dict):
            data = json.dumps(data)
        return self.cipher.encrypt(data.encode())
    
    def decrypt(self, encrypted_data):
        """Decrypt data"""
        decrypted = self.cipher.decrypt(encrypted_data)
        try:
            return json.loads(decrypted.decode())
        except:
            return decrypted.decode()
    
    def save_encrypted_log(self, data, filename):
        """Save encrypted log file"""
        encrypted = self.encrypt(data)
        with open(filename + '.enc', 'wb') as f:
            f.write(encrypted)
        
        # Save metadata (non-sensitive)
        metadata = {
            'timestamp': data.get('timestamp', ''),
            'file': os.path.basename(filename),
            'encrypted': True,
            'size': len(encrypted)
        }
        with open(filename + '.meta', 'w') as f:
            json.dump(metadata, f)
        
        return filename + '.enc'

# Usage example
if __name__ == "__main__":
    encryptor = LogEncryptor()
    
    test_data = {"message": "Sensitive system information"}
    encrypted = encryptor.encrypt(test_data)
    print(f"Encrypted: {encrypted[:50]}...")
    
    decrypted = encryptor.decrypt(encrypted)
    print(f"Decrypted: {decrypted}")
