"""
Application

This module defines a subclass of QApplication to encapsulate application-wide
initialization logic including theme management, styling, splash screen, and
main window loading.
"""

import sys
import os
import darkdetect
import logging
import threading
import site
import importlib
from PyQt5 import QtWidgets, QtGui, QtCore


class Application(QtWidgets.QApplication):
    """
    Custom QApplication with support for user-defined styling and theme selection.
    """

    def __init__(self, sys_argv):
        """
        Initialize the application with system arguments.

        Args:
            sys_argv (list): List of command-line arguments.
        """
        super().__init__(sys_argv)
        self.registry = None
        self.mainwindow = None
        self.ensure_directories_files()

    def ensure_directories_files(self):
        # Ensure necessary user directories exist
        sys.modules["utils"].ensure_directories_exist([
            sys.modules["utils"].PATH_USER_DIR,
            sys.modules["utils"].PATH_SCRIPTS_DIR
        ])

        # Ensure default JSON templates are available in user directory
        sys.modules["utils"].ensure_default_json_files(
            sys.modules["utils"].PATH_REGISTRIES_TEMPLATES_DIR,
            sys.modules["utils"].PATH_USER_DIR,
        )

    def enable_high_dpi_scaling(self):
        """
        Enables high-DPI scaling and high-resolution pixmap support for Qt applications.

        This function sets Qt application attributes to ensure proper scaling and image
        rendering on high-DPI displays. It checks for attribute availability to support
        different versions of PyQt/PySide and should be called before creating the
        QApplication instance.
        """
        if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
            self.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
        if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
            self.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    def set_styling(self):
        """
        Apply application styling including theme-based stylesheet, UI style, and font.
        """
        self.settings = self.registry.get_object('settings')
        self.get_theme()

        qss_path = os.path.join(sys.modules["utils"].PATH_QSS_DIR, f'{self.theme}.qss')

        with open(qss_path, 'r') as f:
            self.setStyleSheet(f.read())

        self.setStyle(self.settings.get("styling").get('style'))
        self.setFont(QtGui.QFont(*self.settings.get("styling").get('font').values()))

    def get_theme(self):
        """
        Determine the active theme based on user or system preference.

        Returns:
            str: The resolved theme ('light' or 'dark').
        """
        self.theme = self.settings.get("styling").get('theme')
        if self.theme == 'System':
            self.theme = 'Dark' if darkdetect.isDark() else 'Light'

    def load_splash(self):
        """
        Load and display the splash screen during application startup.
        """
        self.splash = sys.modules["ui"].SplashScreen()
        self.processEvents()

    def load_mainwindow(self):
        """
        Initialize and display the main application window after splash screen.
        """
        self.mainwindow = sys.modules["ui"].MainWindow()
        self.mainwindow.show()
        self.splash.close()

    def refresh_ui(self, scan_scripts=False, log=False):
        """
        Reload UI components, clearing outdated widgets while preserving dock layout.

        Args:
            scan_scripts (bool): Whether to rescan script inventory after refresh.
        """
        self.mainwindow.save_app_state()

        # Reload site-packages in case new pip packages were installed
        importlib.reload(site)
        site.main()  # Re-adds site-packages to sys.path if needed

        sys.modules['utils'].clear_modules('ui')

        keep_widgets = (QtWidgets.QDialog, type(self.mainwindow.logger_dock))
        for child in self.mainwindow.findChildren(QtWidgets.QWidget, options=QtCore.Qt.FindDirectChildrenOnly):
            if not isinstance(child, keep_widgets):
                child.setParent(None)
                child.deleteLater()

        self.mainwindow.setup_env(scan_scripts)
        self.mainwindow.setup_ui()
        self.mainwindow.apply_settings()
        self.mainwindow.setup_events()
        self.mainwindow.setup_scripts()
        self.mainwindow.restore_app_state()

        self.mainwindow.logger_dock.scroll_logger_to_bottom()

        if log:
            logging.info("MainWindow Refreshed!")

    def start_telemetry_agent(self):
        """
        Start the telemetry logging agent in a background thread using threading.

        This function initializes the LoggingAgent and runs its job loop in a
        daemon thread, which means it will automatically stop when the main
        application exits.

        Args:
            interval_seconds (int): Interval (in seconds) between telemetry uploads.

        """
        try:
            thread = threading.Thread(target=sys.modules["utils"].LoggingAgent, daemon=True)
            thread.start()
            logging.info("Telemetry logging agent thread started.")
        except Exception as e:
            logging.error(f"Failed to start telemetry agent: {e}")

    def start_git_sync(self):
        """
        Starts a background thread to perform the Git synchronization.

        This method initializes a GitSync thread and starts the synchronization process.
        Once the synchronization is complete, the `on_sync_complete` callback is invoked.

        """
        logging.info("Git synchronizing...")
        self.cache = self.registry.get_object('cache')

        if not self.settings.get("git_remotes"):
            return

        self.git_sync_thread = sys.modules["ui"].GitSync(self.settings.get("git_remotes"), self.cache.get("scripts"))
        self.git_sync_thread.script_data_chunk.connect(self.update_cache)
        self.git_sync_thread.finished.connect(lambda: logging.info("Git synchronization complete."))
        self.git_sync_thread.start()

    def update_cache(self, script_data):
        """
        Callback function invoked when the Git sync process is complete.

        This method processes the result of the synchronization and updates the
        cache with the retrieved Git remote data.

        Args:
            result (dict): The result of the Git sync operation, typically containing remote data.

        """
        logging.debug(f"Git synchronization complete for {script_data.get('name')}.")

        self.cache["git_remotes"].update(script_data)
