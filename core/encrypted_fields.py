from django.db import models
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files import File
from .file_encryption import FileEncryptionHandler, EncryptedContentFile, upload_to
import logging

logger = logging.getLogger(__name__)


class DecryptedFile(File):
    """
    A File wrapper that automatically decrypts content when read.
    """
    
    def __init__(self, file, name=None):
        self.encrypted_file = file
        self._decrypted_content = None
        self._is_decrypted = False
        super().__init__(file, name)
    
    def _decrypt_content(self):
        """Decrypt the file content on demand."""
        if not self._is_decrypted:
            try:
                self.encrypted_file.seek(0)
                encrypted_content = self.encrypted_file.read().decode('utf-8')
                self._decrypted_content = FileEncryptionHandler.decrypt_file_content(encrypted_content)
                self._is_decrypted = True
            except Exception as e:
                self._decrypted_content = b''
                self._is_decrypted = True
    
    def read(self, num_bytes=None):
        """Read and return decrypted content."""
        self._decrypt_content()
        if num_bytes is None:
            return self._decrypted_content
        else:
            return self._decrypted_content[:num_bytes]
    
    def __len__(self):
        """Return the size of decrypted content."""
        self._decrypt_content()
        return len(self._decrypted_content)
    
    def seek(self, position):
        """Seek is not supported for decrypted files."""
        pass  # Decrypted content is loaded in memory
    
    def tell(self):
        """Tell is not supported for decrypted files."""
        return 0


class FileEncryptionMixin:
    """
    Mixin for models that have encrypted file fields.
    Add this to your model class to enable automatic file encryption.
    """
    
    def save(self, *args, **kwargs):
        """Override save to encrypt files before saving"""
        # Only process files if this is a new instance or if specific file fields are being updated
        update_fields = kwargs.get('update_fields', None)
        
        # If we're doing a selective update, only process files if file fields are explicitly included
        if update_fields is not None:
            file_fields_to_update = []
            for field in self._meta.get_fields():
                if isinstance(field, (EncryptedFileField, EncryptedImageField)) and field.name in update_fields:
                    file_fields_to_update.append(field)
            
            # Process only the file fields that are being updated
            for field in file_fields_to_update:
                self._process_encrypted_file_field(field)
        else:
            # Process all file fields for new instances or full saves
            for field in self._meta.get_fields():
                if isinstance(field, (EncryptedFileField, EncryptedImageField)):
                    self._process_encrypted_file_field(field)
        
        # Call the original save method
        super().save(*args, **kwargs)
    
    def _process_encrypted_file_field(self, field):
        """Process a single encrypted file field for encryption if needed"""
        try:
            file_attr = getattr(self, field.name)
            
            # Only process if we have a file attribute and it's not already encrypted
            if file_attr and file_attr.name and not file_attr.name.endswith('.enc'):
                # Check if this field has actual file content that needs encryption
                # We need to be very careful here to avoid triggering file access for existing files
                if hasattr(file_attr, '_file') and file_attr._file is not None:
                    # This indicates a new file has been uploaded
                    try:
                        # Read the file content
                        file_attr.file.seek(0)
                        file_content = file_attr.file.read()
                        file_attr.file.seek(0)
                        
                        # Encrypt the file content
                        encrypted_content = FileEncryptionHandler.encrypt_file_content(file_content)
                        
                        # Create encrypted file with .enc extension
                        encrypted_filename = FileEncryptionHandler.get_encrypted_filename(file_attr.name)
                        
                        # Create new encrypted file
                        encrypted_file = ContentFile(encrypted_content.encode('utf-8'))
                        encrypted_file.name = encrypted_filename
                        
                        # Replace the file with encrypted version
                        file_attr.file = encrypted_file
                        file_attr.name = encrypted_filename

                    except Exception as e:
                        import traceback
                        pass
                else:
                    # This is likely an existing file reference, skip processing
                    pass

        except Exception as e:
            import traceback
            pass


class EncryptedFileField(models.FileField):
    """
    A FileField that automatically encrypts files when saved and decrypts when accessed.
    Files are encrypted on disk but appear normal to users.
    """
    
    attr_class = None  # Will be set after EncryptedFieldFile is defined
    
    def __init__(self, verbose_name=None, name=None, **kwargs):
        # For migration compatibility, just use string upload_to paths as-is
        if 'upload_to' not in kwargs:
            kwargs['upload_to'] = 'encrypted_files/'
        super().__init__(verbose_name, name, **kwargs)
        # Set the attr_class after initialization
        self.attr_class = EncryptedFieldFile
    
    def contribute_to_class(self, cls, name, **kwargs):
        """Ensure field is properly set up"""
        super().contribute_to_class(cls, name, **kwargs)
        
        # Add a property to get the decrypted file
        def get_decrypted_file(instance):
            field_file = getattr(instance, self.attname)
            if field_file and field_file.name.endswith('.enc'):
                try:
                    with field_file.open('rb') as f:
                        encrypted_content = f.read().decode('utf-8')
                    decrypted_content = FileEncryptionHandler.decrypt_file_content(encrypted_content)
                    return ContentFile(decrypted_content, name=field_file.name.replace('.enc', ''))
                except Exception as e:
                    pass
            return field_file
        
        setattr(cls, f'{name}_decrypted', property(get_decrypted_file))


class EncryptedImageField(models.ImageField):
    """
    An ImageField that automatically encrypts images when saved and decrypts when accessed.
    Images are encrypted on disk but appear normal to users.
    """
    
    attr_class = None  # Will be set after EncryptedFieldFile is defined
    
    def __init__(self, verbose_name=None, name=None, width_field=None, height_field=None, **kwargs):
        # For migration compatibility, just use string upload_to paths as-is
        if 'upload_to' not in kwargs:
            kwargs['upload_to'] = 'encrypted_files/'
        super().__init__(verbose_name, name, width_field, height_field, **kwargs)
        # Set the attr_class after initialization
        self.attr_class = EncryptedFieldFile
    
    def contribute_to_class(self, cls, name, **kwargs):
        """Ensure field is properly set up"""
        super().contribute_to_class(cls, name, **kwargs)
        
        # Add a property to get the decrypted image
        def get_decrypted_image(instance):
            field_file = getattr(instance, self.attname)
            if field_file and field_file.name.endswith('.enc'):
                try:
                    with field_file.open('rb') as f:
                        encrypted_content = f.read().decode('utf-8')
                    decrypted_content = FileEncryptionHandler.decrypt_file_content(encrypted_content)
                    return ContentFile(decrypted_content, name=field_file.name.replace('.enc', ''))
                except Exception as e:
                    pass
            return field_file
        
        setattr(cls, f'{name}_decrypted', property(get_decrypted_image))


class EncryptedFieldFile(models.fields.files.FieldFile):
    """
    Custom FieldFile that handles encrypted file access.
    """
    
    def _get_file(self):
        """Override to return decrypted file when accessed."""
        if not hasattr(self, '_file') or self._file is None:
            # Get the original file
            self._file = self.storage.open(self.name, 'rb')
            
            # If it's an encrypted file, wrap it with decryption
            if self.name.endswith('.enc'):
                self._file = DecryptedFile(self._file, self.name)
        
        return self._file
    
    def _set_file(self, file):
        """Override to set the file."""
        self._file = file
    
    def _del_file(self):
        """Override to delete the file."""
        if hasattr(self, '_file'):
            del self._file
    
    file = property(_get_file, _set_file, _del_file)
    
    def open(self, mode='rb'):
        """Override to return decrypted content when opening."""
        if self.name.endswith('.enc'):
            # For encrypted files, always return decrypted content
            with self.storage.open(self.name, 'rb') as f:
                encrypted_content = f.read().decode('utf-8')
            decrypted_content = FileEncryptionHandler.decrypt_file_content(encrypted_content)
            return ContentFile(decrypted_content, name=self.name.replace('.enc', ''))
        else:
            # For non-encrypted files, use normal opening
            return self.storage.open(self.name, mode)
    
    def read(self):
        """Read and return decrypted content."""
        if self.name.endswith('.enc'):
            with self.storage.open(self.name, 'rb') as f:
                encrypted_content = f.read().decode('utf-8')
            return FileEncryptionHandler.decrypt_file_content(encrypted_content)
        else:
            with self.storage.open(self.name, 'rb') as f:
                return f.read() 