"""
Biometric device integration utilities for fingerprint scanners
Supports ZKTeco and other common biometric devices
"""
import socket
import struct
import hashlib
import base64
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class BiometricDeviceConnection:
    """Base class for biometric device connections"""

    def __init__(self, ip_address: str, port: int = 4370, timeout: int = 30):
        self.ip_address = ip_address
        self.port = port
        self.timeout = timeout
        self.socket = None
        self.session_id = 0
        self.reply_id = 0

    def connect(self) -> bool:
        """Establish connection to the device"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.ip_address, self.port))
            return True
        except Exception as e:
            return False

    def disconnect(self):
        """Close connection to the device"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None

    def is_connected(self) -> bool:
        """Check if device is connected"""
        return self.socket is not None


class ZKTecoDevice(BiometricDeviceConnection):
    """ZKTeco device integration for fingerprint scanners"""

    # ZKTeco command codes
    CMD_CONNECT = 1000
    CMD_EXIT = 1001
    CMD_ENABLEDEVICE = 1002
    CMD_DISABLEDEVICE = 1003
    CMD_ACK_OK = 2000
    CMD_ACK_ERROR = 2001
    CMD_GET_TIME = 201
    CMD_SET_TIME = 202
    CMD_GET_ATTENDANCE = 110
    CMD_CLEAR_ATTENDANCE = 111
    CMD_GET_USER = 108
    CMD_SET_USER = 109
    CMD_DELETE_USER = 112
    CMD_GET_TEMPLATE = 113
    CMD_SET_TEMPLATE = 114

    def __init__(self, ip_address: str, port: int = 4370):
        super().__init__(ip_address, port)
        self.users = {}
        self.templates = {}
        self.attendance_data = []

    def create_header(self, command: int, session_id: int, reply_id: int, data: bytes = b'') -> bytes:
        """Create ZKTeco protocol header"""
        buf = struct.pack('HHHH', command, 0, session_id, reply_id)
        buf = buf + data

        # Calculate checksum
        checksum = 0
        for i in range(0, len(buf), 2):
            if i == len(buf) - 1:
                checksum += buf[i]
            else:
                checksum += struct.unpack('H', buf[i:i+2])[0]

        reply = struct.pack('HHHH', command, checksum & 0xFFFF, session_id, reply_id)
        return reply + data

    def send_command(self, command: int, data: bytes = b'') -> Optional[bytes]:
        """Send command to device and get response"""
        if not self.is_connected():
            return None

        try:
            header = self.create_header(command, self.session_id, self.reply_id, data)
            self.socket.send(header)

            # Receive response
            response = self.socket.recv(1024)
            if len(response) >= 8:
                cmd, checksum, session_id, reply_id = struct.unpack('HHHH', response[:8])
                return response[8:] if len(response) > 8 else b''

        except Exception as e:

            pass
        return None

    def establish_connection(self) -> bool:
        """Establish session with ZKTeco device"""
        if not self.connect():
            return False

        response = self.send_command(self.CMD_CONNECT)
        if response is not None:
            self.session_id = struct.unpack('H', response[:2])[0] if len(response) >= 2 else 0
            return True

        return False

    def enable_device(self) -> bool:
        """Enable device for normal operations"""
        response = self.send_command(self.CMD_ENABLEDEVICE)
        return response is not None

    def disable_device(self) -> bool:
        """Disable device temporarily (for enrollment etc)"""
        response = self.send_command(self.CMD_DISABLEDEVICE)
        return response is not None

    def get_users(self) -> List[Dict]:
        """Get all users from device"""
        users = []
        response = self.send_command(self.CMD_GET_USER)

        if response:
            # Parse user data (simplified - actual protocol is more complex)
            # This would need proper parsing based on ZKTeco protocol
            pass

        return users

    def enroll_user(self, user_id: int, fingerprint_data: bytes, finger_index: int = 0) -> bool:
        """Enroll user fingerprint"""
        try:
            # Disable device during enrollment
            self.disable_device()

            # Prepare user data
            user_data = struct.pack('HH', user_id, finger_index) + fingerprint_data

            # Send template
            response = self.send_command(self.CMD_SET_TEMPLATE, user_data)

            # Re-enable device
            self.enable_device()

            return response is not None

        except Exception as e:
            self.enable_device()
            return False

    def get_attendance_logs(self, clear_after: bool = False) -> List[Dict]:
        """Get attendance logs from device"""
        logs = []
        response = self.send_command(self.CMD_GET_ATTENDANCE)

        if response:
            # Parse attendance data (simplified)
            # Actual implementation would parse ZKTeco attendance format
            pass

        if clear_after and logs:
            self.clear_attendance_logs()

        return logs

    def clear_attendance_logs(self) -> bool:
        """Clear attendance logs from device"""
        response = self.send_command(self.CMD_CLEAR_ATTENDANCE)
        return response is not None

    def get_device_time(self) -> Optional[datetime]:
        """Get device time"""
        response = self.send_command(self.CMD_GET_TIME)
        if response and len(response) >= 4:
            timestamp = struct.unpack('I', response[:4])[0]
            return datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return None

    def set_device_time(self, dt: datetime = None) -> bool:
        """Set device time"""
        if dt is None:
            dt = timezone.now()

        timestamp = int(dt.timestamp())
        data = struct.pack('I', timestamp)
        response = self.send_command(self.CMD_SET_TIME, data)
        return response is not None


class FingerprintTemplate:
    """Handle fingerprint template operations"""

    @staticmethod
    def encode_template(raw_data: bytes) -> str:
        """Encode fingerprint template for storage"""
        # Add encryption here if needed
        return base64.b64encode(raw_data).decode('utf-8')

    @staticmethod
    def decode_template(encoded_data: str) -> bytes:
        """Decode fingerprint template from storage"""
        return base64.b64decode(encoded_data.encode('utf-8'))

    @staticmethod
    def generate_hash(template_data: bytes) -> str:
        """Generate hash of fingerprint template for verification"""
        return hashlib.sha256(template_data).hexdigest()

    @staticmethod
    def verify_template(template1: bytes, template2: bytes) -> bool:
        """Verify if two templates match"""
        # This would use actual fingerprint matching algorithm
        # For now, simple hash comparison
        return FingerprintTemplate.generate_hash(template1) == FingerprintTemplate.generate_hash(template2)


class BiometricService:
    """High-level service for biometric operations"""

    def __init__(self):
        self.devices = {}

    def add_device(self, device_id: str, ip_address: str, port: int = 4370, device_type: str = 'zkteco'):
        """Add a biometric device"""
        if device_type == 'zkteco':
            device = ZKTecoDevice(ip_address, port)
        else:
            device = BiometricDeviceConnection(ip_address, port)

        self.devices[device_id] = device
        return device

    def get_device(self, device_id: str) -> Optional[BiometricDeviceConnection]:
        """Get device by ID"""
        return self.devices.get(device_id)

    def sync_attendance(self, device_id: str) -> List[Dict]:
        """Sync attendance from a specific device"""
        device = self.get_device(device_id)
        if not device:
            return []

        if isinstance(device, ZKTecoDevice):
            if device.establish_connection():
                logs = device.get_attendance_logs(clear_after=True)
                device.disconnect()
                return logs

        return []

    def enroll_fingerprint(self, device_id: str, user_id: int, finger_data: bytes, finger_index: int = 0) -> bool:
        """Enroll fingerprint on device"""
        device = self.get_device(device_id)
        if not device:
            return False

        if isinstance(device, ZKTecoDevice):
            if device.establish_connection():
                success = device.enroll_user(user_id, finger_data, finger_index)
                device.disconnect()
                return success

        return False

    def sync_all_devices(self) -> Dict[str, List[Dict]]:
        """Sync attendance from all devices"""
        results = {}
        for device_id in self.devices:
            results[device_id] = self.sync_attendance(device_id)
        return results


class MockBiometricDevice:
    """Mock biometric device for testing"""

    def __init__(self):
        self.users = {}
        self.attendance_logs = []

    def enroll_user(self, user_id: int, template_data: str) -> bool:
        """Mock user enrollment"""
        self.users[user_id] = {
            'id': user_id,
            'template': template_data,
            'enrolled_at': timezone.now()
        }
        return True

    def verify_user(self, user_id: int, template_data: str) -> bool:
        """Mock user verification"""
        if user_id in self.users:
            return self.users[user_id]['template'] == template_data
        return False

    def add_attendance_log(self, user_id: int, timestamp: datetime = None):
        """Add mock attendance log"""
        if timestamp is None:
            timestamp = timezone.now()

        self.attendance_logs.append({
            'user_id': user_id,
            'timestamp': timestamp,
            'type': 'clock_in' if len([l for l in self.attendance_logs if l['user_id'] == user_id and l['timestamp'].date() == timestamp.date()]) % 2 == 0 else 'clock_out'
        })

    def get_attendance_logs(self) -> List[Dict]:
        """Get mock attendance logs"""
        return self.attendance_logs.copy()

    def clear_attendance_logs(self):
        """Clear mock attendance logs"""
        self.attendance_logs = []


# Device registry for easy management
device_registry = BiometricService()


def get_biometric_service() -> BiometricService:
    """Get the biometric service instance"""
    return device_registry


def setup_mock_device() -> MockBiometricDevice:
    """Setup mock device for testing"""
    return MockBiometricDevice()