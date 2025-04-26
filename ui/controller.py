"""
Controller

This module defines the Controller class, responsible for wiring QAction
triggers to their corresponding slots or handlers. It encapsulates all event
bindings, keeping the UI logic modular and cleanly decoupled from presentation.
"""

import sys
import shutil


class Controller:
    """
    Manages all QAction event bindings for the application.

    This class centralizes the connections between UI actions and the logic that
    should execute in response. It uses references from the main window to access
    application components and modules dynamically.
    """

    def __init__(self, mainwindow):
        """
        Initializes the Controller.

        Args:
            mainwindow (QMainWindow): The application's main window containing actions, icons, and application references.
        """
        self.mainwindow = mainwindow

    def bind_events(self):
        """
        Connects QAction signals to their respective slot methods.

        All QAction entries are expected to be pre-registered in the main window's
        `actions` dictionary. Event bindings include opening dialogs, executing scripts,
        file navigation, and external tool launching.
        """
        actions = self.mainwindow.actions

        # UI panels & dialogs
        actions['view_code'].triggered.connect(lambda: sys.modules["ui"].ShowCode(self.mainwindow))
        actions['view_readme'].triggered.connect(lambda: sys.modules["ui"].ShowReadme(self.mainwindow))
        actions['open_about_netmig'].triggered.connect(lambda: sys.modules["ui"].ShowAbout(self.mainwindow))
        actions['open_sessions'].triggered.connect(lambda: sys.modules["ui"].NetworkSessionManager(self.mainwindow))
        actions['set_network_session'].triggered.connect(lambda: sys.modules["ui"].SetNetworkSession(self.mainwindow))
        actions['open_inventory'].triggered.connect(lambda: sys.modules["ui"].Inventory(self.mainwindow))
        actions['open_add_script'].triggered.connect(lambda: sys.modules["ui"].AddScript(self.mainwindow))
        actions['open_preferences'].triggered.connect(lambda: sys.modules["ui"].Preferences(self.mainwindow))
        actions['check_updates'].triggered.connect(lambda: sys.modules["ui"].CheckUpdates(self.mainwindow))

        # App and layout control
        actions['refresh'].triggered.connect(lambda: self.mainwindow.app.refresh_ui(log=True))
        actions['reset_view'].triggered.connect(self.mainwindow.reset_view)
        actions['exit'].triggered.connect(lambda: sys.exit(self.mainwindow.app.exit()))

        # Script orchestration
        actions['run_in_terminal'].triggered.connect(lambda: sys.modules["ui"].ScriptExecutor(self.mainwindow).execute())
        actions['abort_script'].triggered.connect(self.mainwindow.script_orch.abort_script)

        # File system actions
        actions['open_user_folder'].triggered.connect(lambda: sys.modules["utils"].open_path(sys.modules["utils"].PATH_USER_DIR))
        actions['open_scripts_folder'].triggered.connect(lambda: sys.modules["utils"].open_path(sys.modules["utils"].PATH_SCRIPTS_DIR))
        actions['open_outputs_folder'].triggered.connect(lambda: sys.modules["utils"].open_path(self.mainwindow.settings.get('output_dir')))

        # Tools
        actions['launch_qtdesigner'].triggered.connect(lambda: sys.modules["utils"].open_path(shutil.which("designer") or "designer"))
        actions['launch_python_shell'].triggered.connect(lambda: sys.modules["utils"].launch_python_shell())
