from rest_framework import serializers
from .timecard_models import Timecard, TimecardEntry
from .models import Employee
from datetime import date, timedelta
import calendar


class TimecardEntrySerializer(serializers.ModelSerializer):
    project_display = serializers.CharField(source='get_project_display', read_only=True)
    project_code = serializers.CharField(source='get_project_code', read_only=True)

    class Meta:
        model = TimecardEntry
        fields = [
            'id', 'date', 'project_name', 'project', 'project_display', 'project_code',
            'timesheet', 'hours', 'is_weekend', 'is_holiday', 'is_billable',
            'activity_description', 'notes'
        ]
        read_only_fields = ['is_weekend', 'project_display', 'project_code']


class TimecardSerializer(serializers.ModelSerializer):
    entries = TimecardEntrySerializer(many=True, read_only=True)
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)

    class Meta:
        model = Timecard
        fields = [
            'id', 'employee', 'employee_name', 'employee_id',
            'year', 'month', 'department', 'position',
            'total_hours', 'approval_status', 'approved_by',
            'approval_date', 'notes', 'entries',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'employee_name', 'employee_id', 'total_hours',
            'approval_date', 'created_at', 'updated_at'
        ]


class TimecardDetailSerializer(TimecardSerializer):
    """Detailed serializer with all entries"""
    entries = TimecardEntrySerializer(many=True, required=False)

    def create(self, validated_data):
        entries_data = validated_data.pop('entries', [])
        timecard = Timecard.objects.create(**validated_data)

        # Create entries for the entire month if not provided
        if not entries_data:
            self.create_month_entries(timecard)
        else:
            for entry_data in entries_data:
                TimecardEntry.objects.create(timecard=timecard, **entry_data)

        return timecard

    def update(self, instance, validated_data):
        entries_data = validated_data.pop('entries', None)

        # Update timecard fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update entries if provided
        if entries_data is not None:
            # Delete existing entries
            instance.entries.all().delete()

            # Create new entries
            for entry_data in entries_data:
                TimecardEntry.objects.create(timecard=instance, **entry_data)

        instance.calculate_total_hours()
        return instance

    def create_month_entries(self, timecard):
        """Create blank entries for all days in the month"""
        year = timecard.year
        month = timecard.month

        # Get number of days in month
        num_days = calendar.monthrange(year, month)[1]

        entries = []
        for day in range(1, num_days + 1):
            entry_date = date(year, month, day)
            entry = TimecardEntry(
                timecard=timecard,
                date=entry_date,
                hours=0,
                project_name=""
            )
            entries.append(entry)

        TimecardEntry.objects.bulk_create(entries)


class TimecardSubmitSerializer(serializers.Serializer):
    """Serializer for submitting timecard for approval"""
    status = serializers.ChoiceField(choices=['submitted', 'approved', 'rejected'])
    notes = serializers.CharField(required=False, allow_blank=True)


class BulkTimecardEntrySerializer(serializers.Serializer):
    """Serializer for bulk updating timecard entries"""
    entries = TimecardEntrySerializer(many=True)

    def validate_entries(self, entries):
        """Ensure all entries belong to the same timecard"""
        if not entries:
            raise serializers.ValidationError("At least one entry is required")
        return entries

    def update(self, timecard, validated_data):
        entries_data = validated_data.get('entries', [])

        # Clear existing entries and create new ones to avoid unique constraint issues
        timecard.entries.all().delete()

        # Create new entries
        for entry_data in entries_data:
            # Skip entries with zero hours and no project
            hours = entry_data.get('hours', 0)
            project_name = entry_data.get('project_name', '').strip()
            project = entry_data.get('project')

            if hours <= 0 and not project_name and not project:
                continue  # Skip empty entries

            TimecardEntry.objects.create(
                timecard=timecard,
                date=entry_data.get('date'),
                project_name=project_name,
                project=project,
                timesheet=entry_data.get('timesheet'),
                hours=hours,
                is_holiday=entry_data.get('is_holiday', False),
                is_billable=entry_data.get('is_billable', True),
                activity_description=entry_data.get('activity_description', ''),
                notes=entry_data.get('notes', '')
            )

        # Recalculate total hours
        timecard.calculate_total_hours()

        return timecard