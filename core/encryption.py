import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError

class EncryptionManager:
    """Manages encryption/decryption operations for sensitive data with support for multiple keys"""
    
    def __init__(self):
        self._primary_fernet = None
        self._backup_fernets = []
        self._initialize_encryption()
    
    def _initialize_encryption(self):
        """Initialize encryption with primary and backup keys from settings"""
        primary_key = getattr(settings, 'ENCRYPTION_KEY', None)
        backup_keys = getattr(settings, 'ENCRYPTION_BACKUP_KEYS', [])
        
        if not primary_key:
            # Use a fixed key for development to ensure consistency
            if settings.DEBUG:
                # Fixed development key - DO NOT USE IN PRODUCTION
                primary_key = "GuanYu-2024-Development-Key-Fixed-For-Consistency"
            else:
                raise ValueError("ENCRYPTION_KEY must be set in production")
        
        # Initialize primary key
        self._primary_fernet = self._derive_key_from_password(primary_key)
        
        # Initialize backup keys
        self._backup_fernets = []
        if isinstance(backup_keys, (list, tuple)):
            for backup_key in backup_keys:
                try:
                    backup_fernet = self._derive_key_from_password(backup_key)
                    self._backup_fernets.append(backup_fernet)
                except Exception as e:
                    pass
        elif backup_keys:  # Single backup key as string
            try:
                backup_fernet = self._derive_key_from_password(backup_keys)
                self._backup_fernets.append(backup_fernet)
            except Exception as e:
                pass
    
    def _derive_key_from_password(self, password):
        """Derive encryption key from password using PBKDF2"""
        if isinstance(password, str):
            password = password.encode('utf-8')
        
        salt = b'GuanYu_salt_2024'  # Use a consistent salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return Fernet(key)
    
    def encrypt(self, plaintext):
        """Encrypt a string or binary value using primary key"""
        if plaintext is None or plaintext == '' or plaintext == b'':
            return plaintext
        
        try:
            # Handle binary data (files)
            if isinstance(plaintext, bytes):
                # Encode binary data to base64 first
                b64_data = base64.b64encode(plaintext).decode('utf-8')
                encrypted = self._primary_fernet.encrypt(b64_data.encode('utf-8'))
                return base64.urlsafe_b64encode(encrypted).decode('utf-8')
            
            # Handle string data (database fields)
            if isinstance(plaintext, str):
                plaintext_bytes = plaintext.encode('utf-8')
            else:
                plaintext_bytes = str(plaintext).encode('utf-8')
            
            encrypted = self._primary_fernet.encrypt(plaintext_bytes)
            return base64.urlsafe_b64encode(encrypted).decode('utf-8')

        except Exception as e:
            raise ValidationError("Failed to encrypt data")
    
    def decrypt(self, ciphertext):
        """Decrypt an encrypted string or binary value, trying primary key first, then backup keys"""
        if ciphertext is None or ciphertext == '' or ciphertext == b'':
            return ciphertext
        
        # Handle both new encrypted format and legacy unencrypted data
        if not self._is_encrypted(ciphertext):
            return ciphertext  # Return as-is if not encrypted
        
        # Try primary key first
        try:
            decoded = base64.urlsafe_b64decode(ciphertext.encode('utf-8'))
            decrypted = self._primary_fernet.decrypt(decoded)
            decrypted_str = decrypted.decode('utf-8')
            
            # Check if this was originally binary data (base64 encoded)
            if self._is_base64(decrypted_str):
                try:
                    # Try to decode from base64 to get original binary data
                    return base64.b64decode(decrypted_str)
                except:
                    # If base64 decode fails, return as string
                    return decrypted_str
            
            return decrypted_str
            
        except Exception as primary_error:
            # Try backup keys if primary fails
            for i, backup_fernet in enumerate(self._backup_fernets):
                try:
                    decoded = base64.urlsafe_b64decode(ciphertext.encode('utf-8'))
                    decrypted = backup_fernet.decrypt(decoded)
                    decrypted_str = decrypted.decode('utf-8')

                    # Check if this was originally binary data (base64 encoded)
                    if self._is_base64(decrypted_str):
                        try:
                            # Try to decode from base64 to get original binary data
                            return base64.b64decode(decrypted_str)
                        except:
                            # If base64 decode fails, return as string
                            return decrypted_str

                    return decrypted_str

                except Exception as backup_error:
                    continue  # Try next backup key

            # If all keys failed, return original (for backward compatibility)
            return ciphertext
    
    def get_key_info(self):
        """Get information about configured keys (for debugging)"""
        info = {
            'primary_key_configured': self._primary_fernet is not None,
            'backup_keys_count': len(self._backup_fernets),
            'total_keys': 1 + len(self._backup_fernets)
        }
        return info
    
    def _is_encrypted(self, value):
        """Check if a value appears to be encrypted"""
        if not isinstance(value, str):
            return False
        try:
            # Try to decode as base64 and check if it's the right length
            decoded = base64.urlsafe_b64decode(value)
            return len(decoded) > 50  # Fernet tokens are typically longer
        except:
            return False
    
    def _is_base64(self, s):
        """Check if a string is valid base64"""
        try:
            if isinstance(s, str):
                # Don't treat phone numbers, emails, or other common data as base64
                # Phone numbers often contain + which is a base64 character
                if s.startswith('+') or '@' in s or len(s) < 16:
                    return False
                
                # Check if string is valid base64
                base64.b64decode(s, validate=True)
                # Check if it looks like base64 (length divisible by 4, valid chars)
                # Also ensure it's long enough to be meaningful base64 data
                return (len(s) % 4 == 0 and 
                        len(s) >= 16 and  # Minimum reasonable base64 length
                        all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' for c in s))
            return False
        except:
            return False


# Global encryption manager instance
encryption_manager = EncryptionManager()


class EncryptedCharField(models.CharField):
    """Custom CharField that automatically encrypts/decrypts data"""
    
    def __init__(self, *args, **kwargs):
        # Store original max_length for validation
        self.original_max_length = kwargs.get('max_length', 255)
        # Increase max_length to accommodate encrypted data
        kwargs['max_length'] = max(kwargs.get('max_length', 255) * 2, 500)
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        """Decrypt value when loading from database"""
        if value is None:
            return value
        return encryption_manager.decrypt(value)
    
    def to_python(self, value):
        """Decrypt value when converting to Python"""
        if value is None:
            return value
        # If value is already decrypted (e.g., from a form), don't decrypt again
        if hasattr(self, '_decrypted_cache') and value in self._decrypted_cache:
            return value
        return encryption_manager.decrypt(value)
    
    def get_prep_value(self, value):
        """Encrypt value before saving to database"""
        if value is None or value == '':
            return value
        
        # Validate length before encryption
        if len(str(value)) > self.original_max_length:
            raise ValidationError(f"Value too long. Maximum length is {self.original_max_length}")
        
        return encryption_manager.encrypt(str(value))
    
    def value_to_string(self, obj):
        """Get a string representation of the value for serialization"""
        value = self.value_from_object(obj)
        return self.get_prep_value(value) if value is not None else ''


class EncryptedTextField(models.TextField):
    """Custom TextField that automatically encrypts/decrypts data"""
    
    def from_db_value(self, value, expression, connection):
        """Decrypt value when loading from database"""
        if value is None:
            return value
        return encryption_manager.decrypt(value)
    
    def to_python(self, value):
        """Decrypt value when converting to Python"""
        if value is None:
            return value
        return encryption_manager.decrypt(value)
    
    def get_prep_value(self, value):
        """Encrypt value before saving to database"""
        if value is None or value == '':
            return value
        return encryption_manager.encrypt(str(value))
    
    def value_to_string(self, obj):
        """Get a string representation of the value for serialization"""
        value = self.value_from_object(obj)
        return self.get_prep_value(value) if value is not None else ''


class EncryptedEmailField(models.EmailField):
    """Custom EmailField that automatically encrypts/decrypts email addresses"""
    
    def __init__(self, *args, **kwargs):
        # Increase max_length to accommodate encrypted data
        kwargs['max_length'] = max(kwargs.get('max_length', 254) * 2, 500)
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        """Decrypt value when loading from database"""
        if value is None:
            return value
        return encryption_manager.decrypt(value)
    
    def to_python(self, value):
        """Decrypt value when converting to Python"""
        if value is None:
            return value
        decrypted = encryption_manager.decrypt(value)
        return super().to_python(decrypted)
    
    def get_prep_value(self, value):
        """Encrypt value before saving to database"""
        if value is None or value == '':
            return value
        # Validate email format first
        validated_value = super().to_python(value)
        return encryption_manager.encrypt(validated_value)
    
    def value_to_string(self, obj):
        """Get a string representation of the value for serialization"""
        value = self.value_from_object(obj)
        return self.get_prep_value(value) if value is not None else ''


class EncryptedDecimalField(models.DecimalField):
    """Custom DecimalField that automatically encrypts/decrypts decimal values"""
    
    def from_db_value(self, value, expression, connection):
        """Decrypt value when loading from database"""
        if value is None:
            return value
        decrypted = encryption_manager.decrypt(value)
        if decrypted == '':
            return None
        return super().to_python(decrypted)
    
    def to_python(self, value):
        """Decrypt value when converting to Python"""
        if value is None:
            return value
        decrypted = encryption_manager.decrypt(str(value))
        return super().to_python(decrypted)
    
    def get_prep_value(self, value):
        """Encrypt value before saving to database"""
        if value is None:
            return value
        # Convert to string first using parent's method
        string_value = super().get_prep_value(value)
        return encryption_manager.encrypt(str(string_value))
    
    def value_to_string(self, obj):
        """Get a string representation of the value for serialization"""
        value = self.value_from_object(obj)
        return self.get_prep_value(value) if value is not None else ''


def encrypt_existing_data(model_class, field_names):
    """
    Utility function to encrypt existing unencrypted data in the database.
    Use this for migrating existing data to encrypted format.
    """
    from django.db import transaction
    
    with transaction.atomic():
        for obj in model_class.objects.all():
            updated = False
            for field_name in field_names:
                value = getattr(obj, field_name)
                if value and not encryption_manager._is_encrypted(str(value)):
                    encrypted_value = encryption_manager.encrypt(str(value))
                    setattr(obj, field_name, encrypted_value)
                    updated = True
            
            if updated:
                obj.save(update_fields=field_names)


# Management command helper
def generate_encryption_key():
    """Generate a new encryption key for use in environment variables"""
    return Fernet.generate_key().decode()


# Security utilities
def mask_sensitive_data(value, mask_char='*', visible_chars=4):
    """Mask sensitive data for display purposes"""
    if not value or len(value) <= visible_chars:
        return value
    
    if len(value) <= visible_chars * 2:
        return mask_char * len(value)
    
    return value[:visible_chars] + mask_char * (len(value) - visible_chars * 2) + value[-visible_chars:]


def validate_encryption_setup():
    """Validate that encryption is properly configured"""
    try:
        test_data = "test_encryption_data"
        encrypted = encryption_manager.encrypt(test_data)
        decrypted = encryption_manager.decrypt(encrypted)

        if decrypted != test_data:
            raise ValueError("Encryption/decryption test failed")

        return True
    except Exception as e:
        return False 