import os
import uuid
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from .encryption import encryption_manager
import logging

logger = logging.getLogger(__name__)


def upload_to(instance, filename):
    """Simple upload function for migration compatibility"""
    return os.path.join('encrypted_files', filename)


class FileEncryptionHandler:
    """Handles encryption and decryption of file contents"""
    
    @staticmethod
    def encrypt_file_content(file_content):
        """
        Encrypt file content (binary data)
        Returns encrypted string that can be stored as text
        """
        try:
            # The encryption manager handles binary data properly
            encrypted_content = encryption_manager.encrypt(file_content)
            return encrypted_content
        except Exception as e:
            raise
    
    @staticmethod
    def decrypt_file_content(encrypted_content):
        """
        Decrypt file content
        Returns original binary data
        """
        try:
            # The encryption manager returns binary data for files
            decrypted_content = encryption_manager.decrypt(encrypted_content)
            return decrypted_content
        except Exception as e:
            raise
    
    @staticmethod
    def get_encrypted_filename(original_filename):
        """
        Generate encrypted filename while preserving some structure
        """
        if not original_filename:
            return f"encrypted_{uuid.uuid4().hex[:8]}.enc"
        
        # Extract name and extension
        name, ext = os.path.splitext(original_filename)
        
        # Create encrypted filename with original extension info preserved
        encrypted_name = f"{name}_{uuid.uuid4().hex[:8]}.enc"
        return encrypted_name
    
    @staticmethod
    def should_encrypt_file(filename):
        """
        Determine if a file should be encrypted based on extension
        """
        if not filename:
            return False
            
        # Define sensitive file extensions that should be encrypted
        sensitive_extensions = {
            # Images
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp',
            # Documents  
            '.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt',
            # Archives and other sensitive files
            '.zip', '.rar', '.7z',
            # Any file without extension (assume sensitive)
        }
        
        ext = os.path.splitext(filename)[1].lower()
        
        # If no extension, encrypt it (assume sensitive)
        if not ext:
            return True
            
        return ext in sensitive_extensions


class EncryptedContentFile(ContentFile):
    """
    A ContentFile that handles encrypted content
    Automatically decrypts content when read
    """
    
    def __init__(self, encrypted_content, name=None):
        self.encrypted_content = encrypted_content
        self.is_decrypted = False
        self._decrypted_content = None
        super().__init__(b'', name)  # Initialize with empty content
    
    def read(self, num_bytes=None):
        """Read and decrypt content on demand"""
        if not self.is_decrypted:
            try:
                self._decrypted_content = FileEncryptionHandler.decrypt_file_content(self.encrypted_content)
                self.is_decrypted = True
            except Exception as e:
                return b''
        
        if num_bytes is None:
            return self._decrypted_content
        else:
            return self._decrypted_content[:num_bytes]
    
    def __len__(self):
        """Return size of decrypted content"""
        if not self.is_decrypted:
            self.read()  # Trigger decryption
        return len(self._decrypted_content) if self._decrypted_content else 0


def create_encrypted_upload_path(subfolder):
    """
    Helper function to create upload_to paths for encrypted files
    """
    def upload_to_func(instance, filename):
        encrypted_filename = FileEncryptionHandler.get_encrypted_filename(filename)
        return os.path.join(subfolder, encrypted_filename)
    return upload_to_func 