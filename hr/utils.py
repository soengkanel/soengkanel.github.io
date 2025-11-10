from django.conf import settings
from cryptography.fernet import Fernet
import base64
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)

def get_encryption_key():
    """Get the encryption key from Django settings."""
    try:
        # Get from Django settings (which loads from .env via django-environ)
        key = settings.ENCRYPTION_KEY
        
        if not key:
            if settings.DEBUG:
                # Generate a new key for development
                key = Fernet.generate_key().decode()
            else:
                raise ValueError("ENCRYPTION_KEY must be set in .env file")
        
        # Convert the key to bytes if it's a string
        if isinstance(key, str):
            key = key.encode()
        
        return key
    except Exception as e:
        raise ValueError("Unable to get encryption key")

def encrypt_field(value):
    """Encrypt a field value."""
    if not value:
        return value
    
    try:
        # Convert value to string if it's not already
        if not isinstance(value, str):
            value = str(value)
        
        # Get the encryption key
        key = get_encryption_key()
        
        # Create a Fernet instance
        f = Fernet(key)
        
        # Encrypt the value
        encrypted_value = f.encrypt(value.encode())
        
        # Return the encrypted value as a string
        return encrypted_value.decode()
    except Exception as e:
        return value

def decrypt_field(value):
    """Decrypt a field value."""
    if not value:
        return value
    
    try:
        # Get the encryption key
        key = get_encryption_key()
        
        # Create a Fernet instance
        f = Fernet(key)
        
        # Decrypt the value
        decrypted_value = f.decrypt(value.encode())
        
        # Return the decrypted value as a string
        return decrypted_value.decode()
    except Exception as e:
        return value 