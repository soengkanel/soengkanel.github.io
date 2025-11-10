"""
Progress tracking utility for long-running import operations.
Stores progress in Django cache for real-time updates.
"""

from django.core.cache import cache
from django.utils import timezone
import uuid
import json


class ImportProgressTracker:
    """Track progress of import operations in real-time."""
    
    def __init__(self, operation_id=None):
        self.operation_id = operation_id or str(uuid.uuid4())
        self.cache_key = f"import_progress_{self.operation_id}"
        self.cache_timeout = 3600  # 1 hour
        
    def start(self, total_items, operation_type="import"):
        """Initialize progress tracking."""
        progress_data = {
            'operation_id': self.operation_id,
            'operation_type': operation_type,
            'status': 'running',
            'total_items': total_items,
            'current_item': 0,
            'processed': 0,
            'skipped': 0,
            'failed': 0,
            'errors': [],
            'current_worker_name': '',
            'stage': 'starting',
            'stage_message': 'Initializing import process...',
            'percentage': 0,
            'started_at': timezone.now().isoformat(),
            'updated_at': timezone.now().isoformat(),
        }
        cache.set(self.cache_key, progress_data, self.cache_timeout)
        return self.operation_id
    
    def update(self, current_item=None, processed=None, skipped=None, failed=None, 
               current_worker_name='', stage=None, stage_message=None, errors=None):
        """Update progress with new values."""
        progress_data = cache.get(self.cache_key)
        if not progress_data:
            return False
            
        # Update provided values
        if current_item is not None:
            progress_data['current_item'] = current_item
        if processed is not None:
            progress_data['processed'] = processed
        if skipped is not None:
            progress_data['skipped'] = skipped
        if failed is not None:
            progress_data['failed'] = failed
        if current_worker_name:
            progress_data['current_worker_name'] = current_worker_name
        if stage:
            progress_data['stage'] = stage
        if stage_message:
            progress_data['stage_message'] = stage_message
        if errors:
            progress_data['errors'].extend(errors if isinstance(errors, list) else [errors])
            # Keep only last 10 errors to prevent cache bloat
            progress_data['errors'] = progress_data['errors'][-10:]
            
        # Calculate percentage
        if progress_data['total_items'] > 0:
            progress_data['percentage'] = min(100, int((progress_data['current_item'] / progress_data['total_items']) * 100))
        
        progress_data['updated_at'] = timezone.now().isoformat()
        
        cache.set(self.cache_key, progress_data, self.cache_timeout)
        return True
    
    def complete(self, success=True, final_message=None):
        """Mark operation as complete."""
        progress_data = cache.get(self.cache_key)
        if not progress_data:
            return False
            
        progress_data['status'] = 'completed' if success else 'failed'
        progress_data['percentage'] = 100
        progress_data['current_item'] = progress_data['total_items']
        
        if final_message:
            progress_data['stage_message'] = final_message
        elif success:
            progress_data['stage_message'] = f"Import completed successfully! Processed {progress_data['processed']} workers."
        else:
            progress_data['stage_message'] = "Import failed. Please check the errors."
            
        progress_data['stage'] = 'completed'
        progress_data['completed_at'] = timezone.now().isoformat()
        progress_data['updated_at'] = timezone.now().isoformat()
        
        cache.set(self.cache_key, progress_data, self.cache_timeout)
        return True
    
    def get_progress(self):
        """Get current progress data."""
        return cache.get(self.cache_key)
    
    def cleanup(self):
        """Clean up progress data from cache."""
        cache.delete(self.cache_key)
    
    @classmethod
    def get_progress_by_id(cls, operation_id):
        """Get progress data by operation ID."""
        cache_key = f"import_progress_{operation_id}"
        return cache.get(cache_key)


# Progress stage constants
class ProgressStages:
    STARTING = 'starting'
    READING_FILE = 'reading_file'
    VALIDATING = 'validating'
    PROCESSING_WORKERS = 'processing_workers'
    PROCESSING_PHOTOS = 'processing_photos'
    SAVING_DATA = 'saving_data'
    FINALIZING = 'finalizing'
    COMPLETED = 'completed'
    FAILED = 'failed'


# Stage messages mapping
STAGE_MESSAGES = {
    ProgressStages.STARTING: 'Initializing import process...',
    ProgressStages.READING_FILE: 'Reading Excel file and extracting data...',
    ProgressStages.VALIDATING: 'Validating worker information...',
    ProgressStages.PROCESSING_WORKERS: 'Processing worker data...',
    ProgressStages.PROCESSING_PHOTOS: 'Processing worker photos and documents...',
    ProgressStages.SAVING_DATA: 'Saving worker data to database...',
    ProgressStages.FINALIZING: 'Finalizing import process...',
    ProgressStages.COMPLETED: 'Import completed successfully!',
    ProgressStages.FAILED: 'Import failed. Please check the errors.',
}