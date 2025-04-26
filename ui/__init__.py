"""
Netmig UI Package Initializer

This module serves as the entry point for the Netmig GUI package. It exposes all
core components of the user interface to simplify imports and enable modular usage.

Included Components:

- Core Application and Main Window
- Dialog Windows for User Interaction
- Icon, Action, Menu, Toolbar, and Status Bar Managers
- Dockable Widgets for Logging, Script Handling, and Execution
- Custom Widgets and Stream Redirection Utilities
- Controller for Signal/Slot Management
- Background Threads for Git and Dependency Tasks
"""

# Core application and window
from .application import Application
from .mainwindow import MainWindow, ScriptOrchestrator
from .controller import Controller

# Dialogs
from .dialogs import (
    SplashScreen,
    ShowCode,
    ShowReadme,
    ShowAbout,
    CheckUpdates,
    Preferences,
    NetworkSessionManager,
    SetNetworkSession,
    AddScript,
    Inventory,
)

# UI building blocks
from .icons import IconManager
from .actions import ActionBuilder
from .menus import MenuBuilder
from .toolbars import ToolbarBuilder
from .statusbar import StatusBar

# Dockable widgets
from .docks import LoggerDock, ScriptsDock, PropsDock, RunnerDock

# Custom widgets
from .widgets import (
    PythonSyntaxHighlighter,
    PasswordField,
    ScriptListButton,
    ScriptExecutor,
    ScriptCard,
    ErrorForm,
    CliForm,
)

# Output stream redirection
from .objects import StdoutStream, StderrStream

# Background threads
from .threads import (
    CheckGitVersion,
    GetRequirements,
    DownloadRepo,
    WaitRestart,
    CheckAuthentication,
    GitSync,
    GitInstaller
)
