from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class DeviceStatus(models.Model):
    """Track passport scanner device status and connection"""
    DEVICE_TYPES = [
        ('PassportReader', 'Passport Reader'),
        ('Scanner', 'Scanner'),
    ]
    
    CONNECTION_STATUS = [
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
        ('error', 'Error'),
    ]
    
    device_name = models.CharField(max_length=255, blank=True)
    device_serial = models.CharField(max_length=255, blank=True)
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPES, default='PassportReader')
    status = models.CharField(max_length=20, choices=CONNECTION_STATUS, default='disconnected')
    version_info = models.CharField(max_length=100, blank=True)
    last_connected = models.DateTimeField(null=True, blank=True)
    websocket_host = models.CharField(max_length=255, default='ws://127.0.0.1:90/echo')
    auto_reconnect = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.device_name or 'Unknown Device'} - {self.get_status_display()}"
    
    class Meta:
        verbose_name = "Device Status"
        verbose_name_plural = "Device Statuses"


class PassportScan(models.Model):
    """Store passport scanning sessions and results"""
    SCAN_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    DOCUMENT_TYPES = [
        ('passport', 'Passport'),
        ('id_card', 'ID Card'),
        ('driver_license', 'Driver License'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='passport_scans')
    scan_id = models.CharField(max_length=100, unique=True)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, default='passport')
    status = models.CharField(max_length=20, choices=SCAN_STATUS, default='pending')
    device_status = models.ForeignKey(DeviceStatus, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Scanning settings
    read_rfid = models.BooleanField(default=True, help_text="Read chip information")
    read_viz = models.BooleanField(default=True, help_text="Read visual zone information")
    enable_rejection = models.BooleanField(default=False)
    enable_callback = models.BooleanField(default=False)
    detect_card_removal = models.BooleanField(default=False)
    
    # Results
    extracted_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Scan {self.scan_id} - {self.get_status_display()}"
    
    def complete_scan(self, extracted_data=None, error_message=None):
        """Mark scan as completed with results"""
        self.completed_at = timezone.now()
        if error_message:
            self.status = 'failed'
            self.error_message = error_message
        else:
            self.status = 'completed'
            if extracted_data:
                self.extracted_data = extracted_data
        self.save()
    
    class Meta:
        verbose_name = "Passport Scan"
        verbose_name_plural = "Passport Scans"
        ordering = ['-started_at']


class ScanImage(models.Model):
    """Store images captured during passport scanning"""
    IMAGE_TYPES = [
        ('White', 'White Light'),
        ('IR', 'Infrared'),
        ('UV', 'Ultraviolet'),
        ('OcrHead', 'OCR Head Photo'),
        ('ChipHead', 'Chip Head Photo'),
        ('SidHead', 'Side Head Photo'),
        ('Full', 'Full Document'),
    ]
    
    scan = models.ForeignKey(PassportScan, on_delete=models.CASCADE, related_name='images')
    image_type = models.CharField(max_length=20, choices=IMAGE_TYPES)
    image_data = models.TextField(help_text="Base64 encoded image data")
    file_path = models.CharField(max_length=500, blank=True, help_text="Optional file storage path")
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.scan.scan_id} - {self.get_image_type_display()}"
    
    class Meta:
        verbose_name = "Scan Image"
        verbose_name_plural = "Scan Images"
        unique_together = ['scan', 'image_type']


class ScanResult(models.Model):
    """Store detailed extraction results from passport scanning"""
    scan = models.OneToOneField(PassportScan, on_delete=models.CASCADE, related_name='result')
    
    # Personal Information
    full_name = models.CharField(max_length=255, blank=True)
    given_names = models.CharField(max_length=255, blank=True)
    surname = models.CharField(max_length=255, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    place_of_birth = models.CharField(max_length=255, blank=True)
    
    # Document Information
    document_number = models.CharField(max_length=100, blank=True)
    document_type = models.CharField(max_length=50, blank=True)
    issuing_country = models.CharField(max_length=100, blank=True)
    issuing_authority = models.CharField(max_length=255, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    
    # MRZ (Machine Readable Zone) Information
    mrz_line1 = models.CharField(max_length=44, blank=True)
    mrz_line2 = models.CharField(max_length=44, blank=True)
    mrz_line3 = models.CharField(max_length=44, blank=True)
    
    # Address (for ID cards)
    address = models.TextField(blank=True)
    
    # Verification Data
    chip_data = models.JSONField(default=dict, blank=True, help_text="RFID chip data")
    ocr_confidence = models.FloatField(null=True, blank=True, help_text="OCR confidence score")
    security_features = models.JSONField(default=dict, blank=True, help_text="Security feature analysis")
    
    # Additional extracted fields
    additional_fields = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Result for {self.scan.scan_id} - {self.full_name or 'Unknown'}"
    
    class Meta:
        verbose_name = "Scan Result"
        verbose_name_plural = "Scan Results"


class WebSocketSession(models.Model):
    """Track WebSocket connections and sessions"""
    session_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='websocket_sessions')
    device_status = models.ForeignKey(DeviceStatus, on_delete=models.CASCADE, related_name='sessions')
    is_active = models.BooleanField(default=True)
    last_ping = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"WS Session {self.session_id} - {self.user.username}"
    
    class Meta:
        verbose_name = "WebSocket Session"
        verbose_name_plural = "WebSocket Sessions"
