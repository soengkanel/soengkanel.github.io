import os
from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environ
env = environ.Env(
    DEBUG=(bool, False),
    DEV_ENV=(bool, False),
    SHOW_ENV_FOOTER=(bool, False),
    SECRET_KEY=(str, ''),
    ALLOWED_HOSTS=(list, []),
    DB_NAME=(str, 'lyp'),
    DB_USER=(str, 'postgres'),
    DB_PASSWORD=(str, ''),
    DB_HOST=(str, 'localhost'),
    DB_PORT=(str, '5432'),
    ENCRYPTION_KEY=(str, ''),
    ENCRYPTION_BACKUP_KEYS=(list, []),
    CARD_REPRINT_CHARGE=(str, '5.00'),
    CARD_LOST_REPLACEMENT_CHARGE=(str, '10.00'),
    CARD_DAMAGED_REPLACEMENT_CHARGE=(str, '5.00'),
)

# Read .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

# Development environment flag (for showing build time footer)
DEV_ENV = env('DEV_ENV')

# Show environment footer (can be enabled in both dev and production)
SHOW_ENV_FOOTER = env('SHOW_ENV_FOOTER')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

# CSRF settings
CSRF_TRUSTED_ORIGINS = [
    'http://lyp:8000',
    'http://127.0.0.1:8000',
    'http://kk.lyp:8000',
    'http://osm.lyp:8000',
    'http://kk.lyp',
    'http://localhost:8000',
    'http://localhost:3000',  # Frontend Next.js app
]

# Additional CSRF settings to prevent failures
CSRF_USE_SESSIONS = True  # Store CSRF tokens in sessions for better consistency

# CORS settings for frontend integration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False

# Allow specific headers that our frontend might send
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
CSRF_COOKIE_AGE = 60 * 60 * 8  # Match session cookie age
CSRF_COOKIE_SAMESITE = 'Lax'  # Match session cookie samesite setting

# Django-tenants configuration (ENABLED for multi-tenancy)
TENANT_MODEL = "company.Company"  # Company model as the tenant
TENANT_DOMAIN_MODEL = "company.Domain"  # Domain model for tenant routing

# SHARED_APPS: Apps that will be in the public schema (shared across all tenants)
SHARED_APPS = [
    'django_tenants',  # Must be first
    # 'tenant_users',  # Global user management - temporarily disabled
    'corsheaders',  # CORS headers for frontend integration
    'django.contrib.admin',
    'django.contrib.auth',  # User authentication in shared schema
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',  # Additional Django management commands
    'widget_tweaks',
    'company',  # Company and Group models
    'user_management',  # User roles and permissions (now global)
    'rest_framework',  # Django REST framework for APIs
    'rest_framework.authtoken',  # Token authentication for REST API
    'django_filters',  # Django filters for REST API
    'drf_spectacular',  # OpenAPI schema generation
    'api',  # REST API module (shared across tenants)
]

# TENANT_APPS: Apps that will be in each tenant's schema
TENANT_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    'qr_code',  # QR code generation
    'core',  # Core functionality (notifications, etc.)
    'zone',  # Worker management
    'hr',  # Employee management
    'dashboard',
    'audit_management',
    'eform',  # Electronic forms
    'landing',
    'document_tracking',  # Document submissions
    'attendance',  # Attendance management module
    'payments',
    'billing',  # Invoicing and billing
    'cards',  # ID card management
    'sinosecu',  # Passport scanner functionality
    'auditlog',
    'policies',  # Policy management
    'project',  # Project management module
    'payroll',  # Payroll management module
    'leave',  # Leave management module
    'expenses',  # Expense management module
    'recruitment',  # Recruitment management module
    'performance',  # Performance management module
    'training',  # Training & Development module
    'employee_portal',  # Employee self-service portal
    'suggestions',  # Suggestion Box module
    'announcements',  # Company Announcements module
]

# Combined INSTALLED_APPS for Django
INSTALLED_APPS = SHARED_APPS + [app for app in TENANT_APPS if app not in SHARED_APPS]

# Multi-tenant middleware (tenant middleware enabled)
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Must be at the top for CORS
    'core.middleware.TenantParameterMiddleware',  # Must be first for django-tenants
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'core.middleware.TenantContextMiddleware',  # Ensure tenant context is properly set
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # Re-enabled with proper API exemptions
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Must be before our custom middleware
    'core.middleware.UserRoleMiddleware',  # Attach role_assignment to user object - after auth
    'zone.signals.CurrentRequestMiddleware',  # Store request in thread local for audit logging
    'core.middleware.SessionSecurityMiddleware',  # Enhanced session security - after auth
    'core.middleware.CSRFSecurityMiddleware',  # Additional CSRF protection
    'auditlog.middleware.AuditlogMiddleware',
    'audit_management.middleware.EnhancedAuditMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    'core.middleware.AdminRoleRestrictionMiddleware' # Middleware protection user role not admin
]

ROOT_URLCONF = 'core.urls'

# Public schema URL configuration (for tenant management)
PUBLIC_SCHEMA_URLCONF = 'core.public_urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.tenant_context',  # Add tenant context
                'core.context_processors.user_role_context',  # Add user role context
                'core.context_processors.sidebar_menu',
                'core.context_processors.notifications_context',
                'core.context_processors.build_time_context',  # Add build time context
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database configuration (Multi-tenant PostgreSQL with schema separation)
DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',  # Multi-tenant PostgreSQL backend
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
    }
}

DATABASE_ROUTERS = (
    'django_tenants.routers.TenantSyncRouter',
)

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Phnom_Penh'  # Cambodia timezone (UTC+7)
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Media files (User uploaded files)
MEDIA_URL = '/media/'
# Use MEDIA_ROOT from environment if set, otherwise use BASE_DIR / 'media'
MEDIA_ROOT = env('MEDIA_ROOT', default=str(BASE_DIR / 'media'))
if not os.path.isabs(MEDIA_ROOT):
    MEDIA_ROOT = BASE_DIR / MEDIA_ROOT

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication settings
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Session settings - Enhanced Security Configuration
# Reduced from 7 days to 8 hours for better security
SESSION_COOKIE_AGE = 60 * 60 * 8  # 8 hours (business day)

# Sessions expire when browser is closed for additional security
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Allow sessions to persist across browser restarts

# Save session on every request to ensure CSRF tokens stay fresh
# This helps prevent CSRF verification failures after periods of activity
SESSION_SAVE_EVERY_REQUEST = True

# Session Security Headers
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookies
SESSION_COOKIE_SAMESITE = 'Lax'  # Less restrictive than 'Strict' to prevent CSRF issues

# Enable secure cookies in production (HTTPS only)
# Uncomment the line below when deploying to production with HTTPS
# SESSION_COOKIE_SECURE = True

# Additional Session Security Settings
SESSION_IDLE_TIMEOUT = 60 * 60 * 2  # 2 hours idle timeout
SESSION_COOKIE_NAME = 'guanyu_sessionid'  # Custom session cookie name
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Use database sessions for security

# Security Headers Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Enable these in production with HTTPS:
# SECURE_SSL_REDIRECT = True
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# Card Printing Charges Settings
CARD_REPRINT_CHARGE = env('CARD_REPRINT_CHARGE')
CARD_LOST_REPLACEMENT_CHARGE = env('CARD_LOST_REPLACEMENT_CHARGE')
CARD_DAMAGED_REPLACEMENT_CHARGE = env('CARD_DAMAGED_REPLACEMENT_CHARGE')

AUTHENTICATION_BACKENDS = (
    # 'tenant_users.permissions.backend.UserBackend',  # Global user authentication - temporarily disabled
    'django.contrib.auth.backends.ModelBackend',
    'user_management.backends.RoleBasedPermissionBackend',  # Our custom role-based permissions
    'guardian.backends.ObjectPermissionBackend',
)

# TODO: Custom User Model will be enabled after migrating FK references across codebase
# AUTH_USER_MODEL = 'user_management.User'

# TODO: django-tenant-users configuration (disabled temporarily)
# TENANT_USERS_DOMAIN = 'localhost'

# Encryption Settings
ENCRYPTION_KEY = env('ENCRYPTION_KEY')
ENCRYPTION_BACKUP_KEYS = env.list('ENCRYPTION_BACKUP_KEYS', default=[])

# Auditlog Configuration (simplified for tenants)
AUDITLOG_INCLUDE_ALL_MODELS = False
AUDITLOG_CID_HEADER = 'HTTP_X_CORRELATION_ID'

# Security Logging Configuration
# Ensure logs directory exists
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'security': {
            'format': '[SECURITY] {asctime} {levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'security_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'security.log'),
            'maxBytes': 1024*1024*10,  # 10 MB
            'backupCount': 5,
            'formatter': 'security',
        },
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'security_console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'security',
        },
    },
    'loggers': {
        'security': {
            'handlers': ['security_console'],  # Start with console only, add file if possible
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Try to add file handler for security logging if possible
try:
    # Test if we can write to the security log file
    security_log_path = os.path.join(LOGS_DIR, 'security.log')
    with open(security_log_path, 'a') as f:
        pass  # Just test if we can open it
    
    # If successful, add file handler to security logger
    LOGGING['loggers']['security']['handlers'].append('security_file')
    
except (PermissionError, FileNotFoundError, OSError):

    
    pass
    # If file logging fails, continue with console logging only
    pass

# Jazzmin settings (admin interface)
JAZZMIN_SETTINGS = {
    "site_title": "GuanYu Admin",
    "site_header": "GuanYu Administration",
    "site_brand": "GuanYu",
    "login_logo": None,
    "login_logo_dark": None,
    "site_logo_classes": "img-circle",
    "site_icon": None,
    "welcome_sign": "Welcome to the GuanYu Admin",
    "copyright": "GuanYu Ltd",
    "search_model": ["auth.User", "hr.Employee", "zone.Worker"],
    "user_avatar": None,

    ############
    # Top Menu #
    ############

    # Links to put along the top menu
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},
        {"model": "auth.User"},
    ],

    #############
    # User Menu #
    #############

    # Additional links to include in the user menu on the top right ("app" url type is not allowed)
    "usermenu_links": [
        {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},
        {"model": "auth.User"}
    ],

    #############
    # Side Menu #
    #############

    # Whether to display the side menu
    "show_sidebar": True,

    # Whether to aut expand the menu
    "navigation_expanded": True,

    # Hide these apps when generating side menu e.g (auth)
    "hide_apps": [],

    # Hide these models when generating side menu (e.g auth.user)
    "hide_models": [],

    # List of apps (and models) to base side menu ordering off of (does not need to contain all apps/models)
    "order_with_respect_to": [
        "auth",
        "hr", 
        "zone",  # Add the zone app first
        "zone.Worker",  # Add Worker model explicitly
        "zone.Zone",
        "zone.WorkerAssignment",
        "zone.WorkerProbationPeriod", 
        "zone.WorkerProbationExtension",
        "zone.Document",  # Worker documents
        "zone.Building",
        "zone.Floor",
        "zone.PermissionCategory",
        "zone.CustomPermission",
        "vip",  # Temporarily added back for migration cleanup
        "cards",
        "billing",
        "document_tracking",
        "eform",
        "audit_management",

        # User Management (Users and Groups)
        "auth.User",
        "auth.Group",
    ],

    # Custom links to append to app groups, keyed on app name
    "custom_links": {
        "zone": [
            {
                "name": "Worker Dashboard", 
                "url": "/zone/dashboard/", 
                "icon": "fas fa-tachometer-alt",
                "permissions": ["zone.view_worker"]
            },
            {
                "name": "Worker Reports", 
                "url": "/zone/reports/", 
                "icon": "fas fa-chart-bar",
                "permissions": ["zone.view_worker"]
            }
        ],
        "hr": [
            {
                "name": "Employee Dashboard", 
                "url": "/hr/dashboard/", 
                "icon": "fas fa-tachometer-alt",
                "permissions": ["hr.view_employee"]
            }
        ]
    },

    # Custom icons for side menu apps/models See https://fontawesome.com/icons?d=gallery&m=free&v=5.0.0,5.0.1,5.0.10,5.0.11,5.0.12,5.0.13,5.0.2,5.0.3,5.0.4,5.0.5,5.0.6,5.0.7,5.0.8,5.0.9,5.1.0,5.1.1,5.2.0,5.3.0,5.3.1,5.4.0,5.4.1,5.4.2,5.5.0,5.6.0,5.6.1,5.6.3,5.7.0,5.7.1,5.7.2,5.8.0,5.8.1,5.8.2,5.9.0,5.10.0,5.10.1,5.10.2,5.11.0,5.11.1,5.11.2,5.12.0,5.12.1,5.13.0,5.13.1,5.14.0,5.15.0,5.15.1,5.15.2,5.15.3,5.15.4&s=solid for free icons
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        
        # Zone app icons
        "zone": "fas fa-map-marked-alt",
        "zone.Worker": "fas fa-hard-hat",
        "zone.Zone": "fas fa-location-dot",
        "zone.Building": "fas fa-building",
        "zone.Floor": "fas fa-layer-group",
        "zone.Document": "fas fa-file-alt",
        "zone.WorkerAssignment": "fas fa-user-tag",
        "zone.WorkerProbationPeriod": "fas fa-clock",
        "zone.WorkerProbationExtension": "fas fa-calendar-plus",
        
        # HR app icons
        "hr": "fas fa-users",
        "hr.Employee": "fas fa-user-tie",
        
        
        
        # Cards app icons
        "cards": "fas fa-id-card",
        "cards.WorkerIDCard": "fas fa-id-badge",
    
        
        # Billing app icons
        "billing": "fas fa-money-bill",
        "billing.Invoice": "fas fa-file-invoice",
        
        # Document tracking icons
        "document_tracking": "fas fa-folder-open",
        "document_tracking.DocumentSubmission": "fas fa-upload",
    },

    # Icons that are used when one is not manually specified
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",

    #################
    # Related Modal #
    #################
    # Use modals instead of popups
    "related_modal_active": False,

    #############
    # UI Tweaks #
    #############
    # Relative paths to custom CSS/JS scripts (must be present in static files)
    "custom_css": None,
    "custom_js": None,
    # Whether to link font from fonts.googleapis.com (use custom_css to supply font otherwise)
    "use_google_fonts_cdn": True,
    # Whether to show the UI customizer on the sidebar
    "show_ui_builder": False,

    ###############
    # Change view #
    ###############
    # Render out the change view as a single form, or in tabs, current options are
    # - single
    # - horizontal_tabs (default)
    # - vertical_tabs
    # - collapsible
    # - carousel
    "changeform_format": "horizontal_tabs",
    # override change forms on a per modeladmin basis
    "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tabs"},
    # Add a language dropdown into the admin
    "language_chooser": False,
}

# Django REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
    'DATE_FORMAT': '%Y-%m-%d',
    'TIME_FORMAT': '%H:%M:%S',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# DRF Spectacular Settings for API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'NextHR Project Management API',
    'DESCRIPTION': 'Comprehensive API for NextHR Project Management System',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,

    # Use CDN versions to avoid static file serving issues
    'SWAGGER_UI_DIST': 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.17.14',
    'SWAGGER_UI_FAVICON_HREF': 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.17.14/favicon-32x32.png',
    'REDOC_DIST': 'https://cdn.jsdelivr.net/npm/redoc@2.1.5/bundles',

    # Disable sidecar to force CDN usage
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': False,
        'filter': True,
        'tryItOutEnabled': True,
    },

    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/v1/endpoints',

    'ENUM_NAME_OVERRIDES': {
        'ProjectStatusEnum': 'project.models.Project.STATUS_CHOICES',
        'ProjectPriorityEnum': 'project.models.Project.PRIORITY_CHOICES',
        'TaskStatusEnum': 'project.models.ProjectTask.STATUS_CHOICES',
        'TaskPriorityEnum': 'project.models.ProjectTask.PRIORITY_CHOICES',
    },

    'SERVERS': [
        {'url': 'http://localhost:8000', 'description': 'Development server'},
        {'url': 'http://127.0.0.1:8000', 'description': 'Local server'},
    ],

    # Additional settings to ensure CDN usage
    'DISABLE_ERRORS_AND_WARNINGS': True,
}
