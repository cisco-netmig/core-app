"""
paths.py

Defines all key filesystem paths used throughout the application.

Organized by:
- Application source directories
- UI resource directories
- User-specific directories (~/.netmig)
- Output directories (outside .netmig)
"""

import os

# === Application Source Directories ===
PATH_APP_DIR = os.path.dirname(os.path.dirname(__file__))              # Root of the application
PATH_APP_DATA = os.path.join(PATH_APP_DIR, '__app__')                   # Application meta deta
PATH_UI_DIR = os.path.join(PATH_APP_DIR, 'ui')                         # UI module directory
PATH_UTILS_DIR = os.path.join(PATH_APP_DIR, 'utils')                   # Utilities module directory
PATH_CODE_TEMPLATES_DIR = os.path.join(PATH_UTILS_DIR, 'templates', 'code')   # Registries Templates
PATH_REGISTRIES_TEMPLATES_DIR = os.path.join(PATH_UTILS_DIR, 'templates', 'registries')   # Registries Templates

# === UI Resource Paths ===
PATH_RESOURCES_DIR = os.path.join(PATH_UI_DIR, 'resources')           # UI resource root
PATH_ICONS_DIR = os.path.join(PATH_RESOURCES_DIR, 'icons')            # Icon assets
PATH_QSS_DIR = os.path.join(PATH_RESOURCES_DIR, 'qss')                # QSS (theme stylesheets)

# === User-Specific Paths (~/.netmig) ===
PATH_USER_DIR = os.path.join(os.path.expanduser('~'), '.netmig')      # Base user directory
PATH_SCRIPTS_DIR = os.path.join(PATH_USER_DIR, 'scripts')             # Installed/local scripts
PATH_SERVER_CACHE_DIR = os.path.join(PATH_USER_DIR, '.servercache')   # Remote inventory cache
PATH_GIT_CACHE_DIR = os.path.join(PATH_USER_DIR, '.gitcache')         # Git repo cache

PATH_SESSION_DATA = os.path.join(PATH_USER_DIR, 'sessions.json')      # Saved network sessions
PATH_SETTINGS_DATA = os.path.join(PATH_USER_DIR, 'settings.json')     # Application settings
PATH_CACHE_DATA = os.path.join(PATH_USER_DIR, 'cache.json')           # App-level general cache

PATH_LOGGER = os.path.join(PATH_USER_DIR, 'logging.log')              # Application log
PATH_LOGGER_TELEMETRY = os.path.join(PATH_USER_DIR, 'telemetry.log')  # Telemetry log

# === Output Paths ===
PATH_SCRIPT_OUTPUTS_DIR = os.path.join(os.path.dirname(PATH_USER_DIR), 'Netmig Outputs')  # User-facing output directory
