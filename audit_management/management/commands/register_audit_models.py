from django.core.management.base import BaseCommand
from django.apps import apps
from django.conf import settings
from auditlog.registry import auditlog
import sys


class Command(BaseCommand):
    help = 'Register important models with audit logging and show audit status'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check',
            action='store_true',
            help='Check which models are currently registered',
        )
        parser.add_argument(
            '--register',
            action='store_true',
            help='Register models from settings',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed information',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('=== Audit Logging Model Registration ===\n')
        )

        if options['check']:
            self.check_registered_models(options['verbose'])
        
        if options['register']:
            self.register_models_from_settings()
        
        if not options['check'] and not options['register']:
            # Default: show both
            self.check_registered_models(options['verbose'])
            self.stdout.write('\n')
            self.register_models_from_settings()

    def check_registered_models(self, verbose=False):
        """Check which models are currently registered with auditlog"""
        self.stdout.write(self.style.HTTP_INFO('📋 Currently Registered Models:'))
        
        registered_models = auditlog.get_models()
        
        if not registered_models:
            self.stdout.write(self.style.WARNING('   No models currently registered!'))
            return
        
        # Group by app
        models_by_app = {}
        for model in registered_models:
            app_label = model._meta.app_label
            if app_label not in models_by_app:
                models_by_app[app_label] = []
            models_by_app[app_label].append(model)
        
        total_count = 0
        for app_label, models in sorted(models_by_app.items()):
            self.stdout.write(f'\n   📁 {app_label}:')
            for model in sorted(models, key=lambda x: x._meta.model_name):
                total_count += 1
                model_name = f'{app_label}.{model._meta.model_name}'
                self.stdout.write(f'      ✅ {model_name}')
                
                if verbose:
                    # Show field configuration
                    fields_info = auditlog.get_model_fields(model)
                    if fields_info['include_fields']:
                        self.stdout.write(f'         Include: {fields_info["include_fields"]}')
                    if fields_info['exclude_fields']:
                        self.stdout.write(f'         Exclude: {fields_info["exclude_fields"]}')
                    if fields_info['mask_fields']:
                        self.stdout.write(f'         Masked: {fields_info["mask_fields"]}')
        
        self.stdout.write(f'\n   📊 Total: {total_count} models registered')

    def register_models_from_settings(self):
        """Register models listed in settings"""
        self.stdout.write(self.style.HTTP_INFO('🔧 Registering Models from Settings:'))
        
        tracking_models = getattr(settings, 'AUDITLOG_INCLUDE_TRACKING_MODELS', [])
        
        if not tracking_models:
            self.stdout.write(self.style.WARNING('   No models configured in AUDITLOG_INCLUDE_TRACKING_MODELS'))
            return
        
        success_count = 0
        error_count = 0
        
        for model_path in tracking_models:
            try:
                app_label, model_name = model_path.split('.')
                model_class = apps.get_model(app_label, model_name)
                
                # Check if already registered
                if auditlog.contains(model_class):
                    self.stdout.write(f'   ⚡ {model_path} (already registered)')
                else:
                    # Register the model
                    auditlog.register(model_class)
                    self.stdout.write(f'   ✅ {model_path} (newly registered)')
                    success_count += 1
                    
            except LookupError:

                    
                pass
                self.stdout.write(
                    self.style.ERROR(f'   ❌ {model_path} (model not found)')
                )
                error_count += 1
            except ValueError as e:
                self.stdout.write(
                    self.style.ERROR(f'   ❌ {model_path} (invalid format: {e})')
                )
                error_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'   ❌ {model_path} (error: {e})')
                )
                error_count += 1
        
        self.stdout.write(f'\n   📊 Registration Summary:')
        self.stdout.write(f'      ✅ Successful: {success_count}')
        if error_count > 0:
            self.stdout.write(f'      ❌ Errors: {error_count}')
        
        # Show important security notice
        self.stdout.write(f'\n   🔒 Security Notice:')
        self.stdout.write(f'      • All registered models will now track changes')
        self.stdout.write(f'      • Sensitive data may be logged (check field configurations)')
        self.stdout.write(f'      • Restart Django server to ensure all middleware is active')

    def get_model_info(self, model_path):
        """Get detailed information about a model"""
        try:
            app_label, model_name = model_path.split('.')
            model_class = apps.get_model(app_label, model_name)
            
            info = {
                'exists': True,
                'model_class': model_class,
                'verbose_name': str(model_class._meta.verbose_name),
                'table_name': model_class._meta.db_table,
                'field_count': len(model_class._meta.fields),
            }
            
            return info
            
        except Exception as e:

            
            pass
            return {'exists': False, 'error': str(e)} 