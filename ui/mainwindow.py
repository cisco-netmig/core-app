"""
Main Window

This module defines the MainWindow class, which serves as the primary UI for
Netmig. It handles UI initialization, script orchestration, docking widgets,
and persistent layout state management.
"""

import sys
import os
import platform
import shutil
import json
import re
import logging
import ctypes
import importlib

from PyQt5 import QtCore, QtWidgets, QtGui


class MainWindow(QtWidgets.QMainWindow):
    """
    Main application window for Netmig.

    Handles script loading, dock setup, styling, event binding,
    and persistent UI state.
    """

    def __init__(self, parent=None):
        """
        Initialize and configure the main window.

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        logging.debug("Initializing MainWindow...")
        self.setup_env(scan_scripts=True)
        self.scan_scripts()
        self.setup_logger()
        self.setup_ui()
        self.runon_startup()
        self.apply_settings()
        self.setup_events()
        self.setup_scripts()
        logging.debug("MainWindow initialization complete.")

    def setup_env(self, scan_scripts):
        """
        Prepare environment paths, output directory, and import custom modules.
        """
        logging.debug("Ensuring directories and reading registry objects.")
        self.app = QtWidgets.QApplication.instance()
        self.app.ensure_directories_files()

        self.cache = self.app.registry.get_object("cache")
        self.settings = self.app.registry.get_object("settings")
        self.sessions = self.app.registry.get_object("sessions")

        self.cache["app_info"] = json.load(open(sys.modules["utils"].PATH_APP_DATA))
        self.cache["app_info"]["readme"] = open(os.path.join(sys.modules["utils"].PATH_APP_DIR, "README.md"),
                                                encoding="utf-8").read()
        self.cache["app_info"]["license"] = open(os.path.join(sys.modules["utils"].PATH_APP_DIR, "LICENSE.txt")).read()

        if not self.settings.get("output_dir"):
            self.settings["output_dir"] = sys.modules["utils"].PATH_SCRIPT_OUTPUTS_DIR
        sys.modules["utils"].ensure_directories_exist([self.settings.get("output_dir")])
        logging.debug(f"Output directory set: {self.settings['output_dir']}")

        for path in self.settings.get("sys_paths"):
            abs_path = os.path.abspath(path)
            sys.path.append(abs_path)
            sys.modules["utils"].import_from_path(os.path.basename(path), abs_path)
        logging.debug(f"System paths imported: {self.settings.get('sys_paths')}")

        if scan_scripts:
            self.scan_scripts()

        logging.debug("Environment setup complete.")

    def scan_scripts(self):
        """
        Load and cache script metadata from disk.

        Args:
            scan_scripts (bool): Whether to rescan scripts from the file system.
        """
        logging.debug("Scanning for scripts...")
        scripts = sys.modules["utils"].build_script_registry(sys.modules["utils"].PATH_SCRIPTS_DIR)
        for script_id, script_data in scripts.items():
            if not self.cache.get("scripts").get(script_id):
                self.cache["scripts"][script_id] = {"load": True, "source": "local"}
            self.cache["scripts"][script_id].update(script_data)
            logging.debug(f"Script {script_id} added to cache.")

    def setup_logger(self):
        """
        Add the logger dock widget to the main window.
        """
        self.logger_dock = sys.modules["ui"].LoggerDock(self)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.logger_dock)
        logging.debug("LoggerDock added to bottom dock area.")

    def setup_ui(self):
        """
        Construct the main UI layout including docks, menus, toolbars, and central widgets.
        """
        logging.debug("Building UI layout components...")
        self.script_orch = sys.modules["ui"].ScriptOrchestrator(self)

        self.icon_manager = sys.modules["ui"].IconManager()
        self.icons = self.icon_manager.load_icons()

        self.action_builder = sys.modules["ui"].ActionBuilder(self)
        self.actions = self.action_builder.create_actions()

        self.menu_builder = sys.modules["ui"].MenuBuilder(self)
        self.menus = self.menu_builder.create_menus()
        self.menu_builder.add_to_mainwindow()

        self.toolbar_builder = sys.modules["ui"].ToolbarBuilder(self)
        self.toolbars = self.toolbar_builder.create_toolbars()
        self.toolbar_builder.add_to_mainwindow()

        self.status_bar = sys.modules["ui"].StatusBar(self)
        self.setStatusBar(self.status_bar)

        self.scripts_dock = sys.modules["ui"].ScriptsDock(self)
        self.scripts_dock.script_orch = self.script_orch
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.scripts_dock)

        self.props_dock = sys.modules["ui"].PropsDock(self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.props_dock)

        self.central_widget = QtWidgets.QWidget(self)
        self.central_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setSpacing(0)

        self.runner_dock = sys.modules["ui"].RunnerDock(self)
        self.central_layout.addWidget(self.runner_dock)
        self.setCentralWidget(self.central_widget)

        self.action_builder.bind_view_actions_to_docks()
        logging.debug("Docks, menu, toolbar, and central layout initialized.")

        self.app.set_styling()
        self.setWindowTitle("Netmig")
        self.setWindowIcon(self.icons["netmig"])
        self.setWindowState(QtCore.Qt.WindowState.WindowMaximized)
        logging.debug("Main window title, icon, and maximized state set.")

        self.app.focusChanged.connect(self.update_status)

        self.restore_app_state()
        logging.debug("App state restored.")

    def update_status(self, old, now):
        """
        Updates the application's status bar with a context-aware message based on focus change.
        """
        if not now:
            return

        current = now
        while current:
            if isinstance(current, (QtWidgets.QDialog, QtWidgets.QDockWidget)):
                title = current.windowTitle()
                object_name = current.objectName()

                parts = ["Netmig", "Runner"] if "Runner" in object_name else ["Netmig"]
                if title:
                    parts.append(title)

                self.status_bar.showMessage(" > ".join(parts))
                break
            current = current.parent()

    def runon_startup(self):
        if self.settings.get("load_all_scripts"):
            for script_id in self.cache["scripts"]:
                self.cache["scripts"][script_id].update(load=True)

        # self.app.start_git_sync()
        # self.app.start_scp_sync()

    def apply_settings(self):
        logging_level = self.settings.get("logging_level")
        self.logger_dock.logger.setLevel(getattr(logging, logging_level, logging.INFO))
        logging.debug(f"Logger level set to {logging_level}")

        self.status_bar.logging_button.setText(logging_level)
        self.status_bar.logging_button.setStyleSheet(
            f'QPushButton {{color:{self.logger_dock.format_colors.get(logging_level)};}}')
        self.status_bar.stream_button.setText(self.settings.get("logging_stream"))
        self.status_bar.telemetry_button.setText("Active" if self.settings.get("telemetry_enabled") else "Inactive")
        self.status_bar.version_button.setText(f"Version {self.cache['app_info']['version']}")
        logging.debug("Status bar logging stream and version set.")

    def setup_events(self):
        """
        Register UI events and initialize the controller for action bindings.
        """
        self.controller = sys.modules["ui"].Controller(self)
        self.controller.bind_events()
        logging.debug("Controller events bound.")

    def setup_scripts(self):
        """
        Load registered scripts and attach them to docks.
        """
        logging.debug("Loading scripts into docks...")
        self.script_orch.load_scripts()

        curr_script_id = self.cache["run_time"].get("curr_script_id")
        curr_script_info = self.cache["scripts"].get(curr_script_id)

        if curr_script_id and curr_script_info and curr_script_info.get("load"):
            self.script_orch.set_active(curr_script_id)
        else:
            script_id = next((k for k, v in self.cache["scripts"].items() if v.get("load")), None)
            if script_id:
                self.script_orch.set_active(script_id)

        logging.debug(f"Active script set to: {self.script_orch.curr_script_id}")

    def reset_view(self):
        """
        Reset layout to default configuration and reload the UI.
        """

        # Clear any saved state
        logging.debug("Resetting application layout to default.")
        self.settings["app_state"].update({})

        # Reset Dock Widgets
        self.removeDockWidget(self.logger_dock)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.logger_dock)
        self.logger_dock.setFloating(False)
        self.logger_dock.show()

        self.removeDockWidget(self.scripts_dock)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.scripts_dock)
        self.scripts_dock.setFloating(False)
        self.scripts_dock.show()

        self.removeDockWidget(self.props_dock)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.props_dock)
        self.props_dock.setFloating(False)
        self.props_dock.show()

        for toolbar in self.findChildren(QtWidgets.QToolBar):
            self.removeToolBar(toolbar)
        self.toolbar_builder.create_toolbars()
        self.toolbar_builder.add_to_mainwindow()
        logging.debug("Toolbars and docks reinitialized.")

        logging.info("Layout and toolbars reset to default.")

    def save_app_state(self):
        """
        Save window geometry, state, and scroll positions to the registry.
        """
        app_state = {
            'geometry': self.saveGeometry().toBase64().data().decode(),
            'window_state': self.saveState().toBase64().data().decode(),
            'scroll': {},
            'focus_widget': self.focusWidget().objectName() if self.focusWidget() else ""
        }

        for scroll_area in self.findChildren(QtWidgets.QAbstractScrollArea):
            if scroll_area.objectName():
                app_state['scroll'][scroll_area.objectName()] = {
                    'h': scroll_area.horizontalScrollBar().value(),
                    'v': scroll_area.verticalScrollBar().value()
                }
        self.settings["app_state"] = app_state
        logging.debug("Application state saved to settings.")

    def restore_app_state(self):
        """
        Restore geometry, dock state, scroll positions, and focus from the registry.
        """
        logging.debug("Restoring saved application layout and state.")
        if geometry_b64 := self.settings["app_state"].get("geometry"):
            self.restoreGeometry(QtCore.QByteArray.fromBase64(geometry_b64.encode()))

        if window_state_b64 := self.settings["app_state"].get("window_state"):
            self.restoreState(QtCore.QByteArray.fromBase64(window_state_b64.encode()))

        for scroll_area in self.findChildren(QtWidgets.QAbstractScrollArea):
            if scroll_area.objectName():
                scroll = self.settings["app_state"].get("scroll", {}).get(scroll_area.objectName(), {})
                if h := scroll.get("h"):
                    scroll_area.horizontalScrollBar().setValue(h)
                if v := scroll.get("v"):
                    scroll_area.verticalScrollBar().setValue(v)

        if focus_name := self.settings["app_state"].get("focus_widget"):
            if focus_widget := self.findChild(QtWidgets.QWidget, focus_name):
                focus_widget.setFocus()
        logging.debug("Geometry, window state, and scroll positions applied.")

    def contextMenuEvent(self, event):
        """
        Override to display the Actions menu on right-click in main window.

        Args:
            event (QContextMenuEvent): Right-click event.
        """
        self.menus.get("Actions").exec_(self.mapToGlobal(event.pos()))
        logging.debug("Context menu event triggered.")

    def closeEvent(self, event):
        """
        Save UI state before closing the application.

        Args:
            event (QCloseEvent): Window close event.
        """
        self.save_app_state()
        event.accept()
        logging.debug("Closing application. State saved.")


class ScriptOrchestrator:
    """
    Coordinates script management between the UI components.

    Manages currently active script details, loads scripts into dock panels,
    and handles form activation.
    """

    def __init__(self, mainwindow):
        """
        Initialize the orchestrator.

        Args:
            mainwindow (MainWindow): Reference to the main application window.
        """
        self.mainwindow = mainwindow
        self.curr_script_id = None
        self.curr_script_name = None
        self.curr_module_path = None
        self.curr_script_readme_path = None
        self.curr_script_main_path = None
        self.curr_script_form = None
        self.curr_script_session = None

    def load_scripts(self):
        """
        Add all scripts marked for loading to the scripts and runner docks.
        """
        self.mainwindow.scripts_dock.script_button_list.clear()
        for script_id, script_data in self.mainwindow.cache["scripts"].items():
            if not script_data.get("load"):
                logging.debug(f"Skipping unloaded script: {script_id}")
                continue
            self.mainwindow.scripts_dock.add_script(script_id, script_data)
            self.mainwindow.runner_dock.add_script(script_id, script_data)
            logging.debug(f"Loaded script into docks: {script_id}")

    def set_active(self, script_id):
        """
        Set a script as the currently active script.

        Args:
            script_id (str): ID of the script to activate.
        """
        logging.debug(f"Setting active script: {script_id}")
        self.curr_script_id = script_id
        self.curr_script_name = self.mainwindow.cache["scripts"][script_id]["name"]
        self.curr_module_path = self.mainwindow.cache["scripts"][script_id]["module"]
        self.curr_script_readme_path = os.path.join(self.curr_module_path, "README.md")
        self.curr_script_form = self.mainwindow.runner_dock.form_stack.map.get(script_id, {}).get("form")
        self.curr_script_session = self.mainwindow.cache["scripts"][script_id].get("session", "")
        self.mainwindow.scripts_dock.set_active(script_id)
        self.mainwindow.runner_dock.set_active(script_id)
        self.mainwindow.props_dock.set_active(self.mainwindow.cache["scripts"][script_id])
        self.mainwindow.cache["run_time"]["curr_script_id"] = self.curr_script_id

        logging.debug(f"Active script data: name={self.curr_script_name}, path={self.curr_module_path}")

    def abort_script(self):
        """
        Attempt to abort the currently active script if it supports `__abort__`.
        """
        try:
            if self.curr_script_form and hasattr(self.curr_script_form, "__abort__"):
                logging.info(f"Aborting script: {self.curr_script_name}")
                self.curr_script_form.__abort__()
            else:
                logging.warning(f"Abort not supported for script: {self.curr_script_name}")
        except Exception as e:
            logging.error(f"Error during script abort: {e}")
