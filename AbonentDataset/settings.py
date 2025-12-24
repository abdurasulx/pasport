"""
Django settings for AbonentDataset project.

Abonentlarning pasport ma'lumotlarini to'plash uchun dataset.
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-va__69-nx(od2_*vzk*e1^(g2c5=#hq4h&@pqc84=d9s1_$(k+'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# =============================================================================
# JAZZMIN CONFIGURATION - Modern Admin UI
# =============================================================================

JAZZMIN_SETTINGS = {
    # Sarlavha va branding
    "site_title": "AbonentDataset Admin",
    "site_header": "AbonentDataset",
    "site_brand": "AbonentDataset",
    "site_logo": None,
    "login_logo": None,
    "site_logo_classes": "img-circle",
    "site_icon": None,
    
    # Welcome text
    "welcome_sign": "AbonentDataset Admin Paneliga Xush Kelibsiz",
    
    # Copyright
    "copyright": "AbonentDataset © 2024",
    
    # Search model
    "search_model": ["abonents.Abonent"],
    
    # User avatar
    "user_avatar": None,
    
    # Top menu links
    "topmenu_links": [
        {"name": "Bosh sahifa", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "API", "url": "/api/", "new_window": True},
        {"model": "abonents.Abonent"},
    ],
    
    # User menu links
    "usermenu_links": [
        {"name": "API Dokumentatsiya", "url": "/api/", "new_window": True},
        {"model": "auth.user"}
    ],
    
    # Side menu
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    
    # Custom icons for apps/models
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "abonents.Abonent": "fas fa-id-card",
    },
    
    # Default icons
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    
    # Related modal
    "related_modal_active": False,
    
    # UI Tweaks
    "custom_css": None,
    "custom_js": None,
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    
    # Change view
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
    },
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}


# =============================================================================
# APPLICATION DEFINITION
# =============================================================================

INSTALLED_APPS = [
    # Jazzmin MUST be before django.contrib.admin
    'jazzmin',
    
    # Django core apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'django_filters',
    
    # Local apps
    'abonents',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'AbonentDataset.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'AbonentDataset.wsgi.application'


# =============================================================================
# DATABASE
# =============================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# =============================================================================
# PASSWORD VALIDATION
# =============================================================================

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


# =============================================================================
# INTERNATIONALIZATION
# =============================================================================

LANGUAGE_CODE = 'uz'

TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

USE_TZ = True


# =============================================================================
# STATIC FILES
# =============================================================================

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'


# =============================================================================
# MEDIA FILES (Rasmlar uchun)
# =============================================================================

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# =============================================================================
# DEFAULT PRIMARY KEY
# =============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

APPEND_SLASH = True

# =============================================================================
# DJANGO REST FRAMEWORK CONFIGURATION
# =============================================================================

REST_FRAMEWORK = {
    # Pagination
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    
    # Filter backends
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    
    # Parsers
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
    
    # Renderers
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    
    # Authentication (optional - Token auth)
    # 'DEFAULT_AUTHENTICATION_CLASSES': [
    #     'rest_framework.authentication.TokenAuthentication',
    #     'rest_framework.authentication.SessionAuthentication',
    # ],
    
    # Permissions (default: AllowAny for development)
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}
