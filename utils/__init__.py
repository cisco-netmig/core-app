"""
utils package initializer.

This package provides a collection of utility classes and functions used throughout the application,
including support for:

- Centralized registry for managing multiple data sources (`Registry`)
- Persistent key-value storage with auto-save (`PersistentDict`)
- Ensuring existence of required directories and default JSON templates
- Markdown processing utilities (`md_to_plain`, `md_to_html`)
- File path helpers and dynamic imports
- Launching embedded Python shells
- Script registry building
- Secure file transfer over SCP (`SCPClient`)

These utilities are used across the application and are exposed here for convenient imports.
"""

from .helpers import (
    ensure_default_json_files,
    ensure_directories_exist,
    md_to_plain,
    md_to_html,
    open_path,
    import_from_path,
    launch_python_shell,
    build_script_registry,
    clear_modules
)
from .registry import (
    Registry,
    PersistentDict
)
from .paths import *
from .scp import SCPClient
from .telemetry import LoggingAgent
