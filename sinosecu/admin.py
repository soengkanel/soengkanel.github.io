from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import DeviceStatus, PassportScan, ScanImage, ScanResult, WebSocketSession


@admin.register(DeviceStatus)
class DeviceStatusAdmin(admin.ModelAdmin):
    list_display = ['device_name', 'device_type', 'status', 'version_info', 'last_connected', 'auto_reconnect']
    list_filter = ['device_type', 'status', 'auto_reconnect']
    search_fields = ['device_name', 'device_serial']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Device Information', {
            'fields': ('device_name', 'device_serial', 'device_type', 'version_info')
        }),
        ('Connection', {
            'fields': ('status', 'websocket_host', 'auto_reconnect', 'last_connected')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


class ScanImageInline(admin.TabularInline):
    model = ScanImage
    extra = 0
    readonly_fields = ['created_at']
    fields = ['image_type', 'width', 'height', 'file_path', 'created_at']


class ScanResultInline(admin.StackedInline):
    model = ScanResult
    extra = 0
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('full_name', 'given_names', 'surname', 'gender', 'nationality', 
                      'date_of_birth', 'place_of_birth')
        }),
        ('Document Information', {
            'fields': ('document_number', 'document_type', 'issuing_country', 
                      'issuing_authority', 'issue_date', 'expiry_date')
        }),
        ('Address & MRZ', {
            'fields': ('address', 'mrz_line1', 'mrz_line2', 'mrz_line3')
        }),
        ('Verification Data', {
            'fields': ('chip_data', 'ocr_confidence', 'security_features', 'additional_fields'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(PassportScan)
class PassportScanAdmin(admin.ModelAdmin):
    list_display = ['scan_id', 'user', 'document_type', 'status', 'started_at', 'completed_at', 'scan_duration', 'view_detail_link']
    list_filter = ['status', 'document_type', 'started_at', 'read_rfid', 'read_viz']
    search_fields = ['scan_id', 'user__username', 'user__email']
    readonly_fields = ['scan_id', 'started_at', 'completed_at', 'scan_duration']
    inlines = [ScanImageInline, ScanResultInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('scan_id', 'user', 'document_type', 'status', 'device_status')
        }),
        ('Scanning Settings', {
            'fields': ('read_rfid', 'read_viz', 'enable_rejection', 'enable_callback', 'detect_card_removal')
        }),
        ('Results', {
            'fields': ('extracted_data', 'error_message')
        }),
        ('Timestamps', {
            'fields': ('started_at', 'completed_at', 'scan_duration'),
            'classes': ('collapse',)
        })
    )
    
    def scan_duration(self, obj):
        """Calculate and display scan duration"""
        if obj.completed_at and obj.started_at:
            duration = obj.completed_at - obj.started_at
            total_seconds = int(duration.total_seconds())
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes}m {seconds}s"
        return "-"
    scan_duration.short_description = "Duration"
    
    def view_detail_link(self, obj):
        """Link to view scan detail in frontend"""
        from django.urls import reverse
        try:
            url = reverse('sinosecu:scan_detail', args=[obj.scan_id])
            return format_html('<a href="{}" target="_blank">View Detail</a>', url)
        except:
            return "-"
    view_detail_link.short_description = "Detail"
    view_detail_link.allow_tags = True
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'device_status')


@admin.register(ScanImage)
class ScanImageAdmin(admin.ModelAdmin):
    list_display = ['scan', 'image_type', 'width', 'height', 'created_at', 'file_size_display']
    list_filter = ['image_type', 'created_at']
    search_fields = ['scan__scan_id', 'image_type']
    readonly_fields = ['created_at', 'file_size_display']
    
    def file_size_display(self, obj):
        """Display the approximate size of base64 image data"""
        if obj.image_data:
            # Approximate size calculation (base64 encoding adds ~33% overhead)
            size_bytes = len(obj.image_data) * 3 / 4
            if size_bytes > 1024 * 1024:
                return f"{size_bytes / (1024 * 1024):.1f} MB"
            elif size_bytes > 1024:
                return f"{size_bytes / 1024:.1f} KB"
            else:
                return f"{size_bytes:.0f} bytes"
        return "-"
    file_size_display.short_description = "Size"


@admin.register(ScanResult)
class ScanResultAdmin(admin.ModelAdmin):
    list_display = ['scan', 'full_name', 'document_number', 'nationality', 'date_of_birth', 'created_at']
    list_filter = ['nationality', 'document_type', 'issuing_country', 'created_at']
    search_fields = ['full_name', 'document_number', 'scan__scan_id']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('full_name', 'given_names', 'surname', 'gender', 'nationality', 
                      'date_of_birth', 'place_of_birth')
        }),
        ('Document Information', {
            'fields': ('document_number', 'document_type', 'issuing_country', 
                      'issuing_authority', 'issue_date', 'expiry_date')
        }),
        ('Address & MRZ', {
            'fields': ('address', 'mrz_line1', 'mrz_line2', 'mrz_line3')
        }),
        ('Verification Data', {
            'fields': ('chip_data', 'ocr_confidence', 'security_features', 'additional_fields'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(WebSocketSession)
class WebSocketSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user', 'device_status', 'is_active', 'last_ping', 'session_duration']
    list_filter = ['is_active', 'created_at', 'last_ping']
    search_fields = ['session_id', 'user__username']
    readonly_fields = ['created_at', 'session_duration']
    
    def session_duration(self, obj):
        """Calculate session duration"""
        if obj.last_ping and obj.created_at:
            duration = obj.last_ping - obj.created_at
            total_seconds = int(duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            if hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
        return "-"
    session_duration.short_description = "Duration"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'device_status')


# Admin site customizations
admin.site.site_header = "Sinosecu Passport Scanner Administration"
admin.site.site_title = "Sinosecu Admin"
admin.site.index_title = "Passport Scanner Management"
