"""
Action Builder

Defines the ActionBuilder class responsible for constructing and managing QAction
instances with associated icons and properties. It also includes methods to bind
UI actions to dock widget visibility toggles.
"""

import os
from PyQt5 import QtWidgets, QtGui, QtCore


class ActionBuilder:
    """
    Constructs and manages QAction objects with associated icons and settings.
    """

    ACTIONS = {
        "open_inventory": {"icon.Off": "inventory", "text": "Inventory"},
        "open_add_script": {"icon.Off": "new-file", "text": "Add Script"},
        "open_about_netmig": {"icon.Off": "netmig", "text": "About Netmig"},
        "generate_telemetry": {"icon.Off": "event-log", "text": "Generate Telemetry"},
        "check_updates": {"icon.Off": "cloud-sync", "text": "Check for updates"},
        "exit": {"icon.Off": "exit", "text": "Exit"},
        "view_runner": {"icon.Off": "unchecked", "icon.On": "checked", "text": "Runner", "checkable": True, "checked": True},
        "view_scripts": {"icon.Off": "unchecked", "icon.On": "checked", "text": "Scripts", "checkable": True, "checked": True},
        "view_props": {"icon.Off": "unchecked", "icon.On": "checked", "text": "Properties", "checkable": True, "checked": True},
        "view_logger": {"icon.Off": "unchecked", "icon.On": "checked", "text": "Logger", "checkable": True, "checked": True},
        "open_preferences": {"icon.Off": "preferences", "text": "Preferences"},
        "open_sessions": {"icon.Off": "connection", "text": "Sessions"},
        "open_user_folder": {"icon.Off": "user-folder", "text": "User Folder"},
        "open_scripts_folder": {"icon.Off": "code-folder", "text": "Scripts Folder"},
        "open_outputs_folder": {"icon.Off": "product-documents", "text": "Outputs Folder"},
        "refresh": {"icon.Off": "refresh", "text": "Refresh"},
        "abort_script": {"icon.Off": "Esc", "text": "Abort"},
        "set_network_session": {"icon.Off": "broadcasting", "text": "Set Session"},
        "view_code": {"icon.Off": "code", "text": "View Code"},
        "view_readme": {"icon.Off": "about", "text": "View Readme"},
        "run_in_terminal": {"icon.Off": "terminal", "text": "Run in Terminal"},
        "launch_qtdesigner": {"icon.Off": "qt-logo", "text": "Qt Designer"},
        "launch_python_shell": {"icon.Off": "python-interpreter", "text": "Python Shell"},
        "reset_view": {"icon.Off": "reset", "text": "Reset View"},
    }

    def __init__(self, mainwindow):
        """
        Initialize the ActionBuilder.

        Args:
            mainwindow (QMainWindow): Reference to the main application window.
        """
        self.mainwindow = mainwindow
        self.actions = {}

    def create_actions(self):
        """
        Creates QAction objects from the ACTIONS dictionary.

        Returns:
            dict: A dictionary mapping action names to QAction instances.
        """
        for name, props in self.ACTIONS.items():
            action = QtWidgets.QAction()
            action.setText(props.get("text", name))
            action.setCheckable(props.get("checkable", False))
            action.setChecked(props.get("checked", False))

            icon = QtGui.QIcon()
            icon_off = self.mainwindow.icons.get(props.get("icon.Off"))
            icon_on = self.mainwindow.icons.get(props.get("icon.On"))

            # Add both off/on states to the icon if available
            if icon_off:
                icon.addPixmap(icon_off.pixmap(30, 30), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            if icon_on:
                icon.addPixmap(icon_on.pixmap(30, 30), QtGui.QIcon.Normal, QtGui.QIcon.On)

            action.setIcon(icon)

            # Store icons for dynamic updates
            action._icon_on = icon_on
            action._icon_off = icon_off

            self.actions[name] = action

        return self.actions

    def bind_view_actions_to_docks(self):
        """
        Binds toggleable view actions to their corresponding dock widgets.
        Prevents hidden QDockWidgets after minimize/maximize.
        """
        docks = {
            "runner": self.mainwindow.runner_dock,
            "scripts": self.mainwindow.scripts_dock,
            "props": self.mainwindow.props_dock,
            "logger": self.mainwindow.logger_dock,
        }

        for key, dock in docks.items():
            action_key = f"view_{key}"
            action = self.actions.get(action_key)

            if not action or not isinstance(dock, QtWidgets.QDockWidget):
                continue

            # Manually ensure dock is visible initially if action is checked
            if action.isChecked():
                dock.show()
            else:
                dock.hide()

            # Avoid feedback loop using wrapper
            def toggle_dock(checked, d=dock):
                d.setVisible(checked)

            def sync_action(visible, a=action):
                # Avoid signal loop
                a.blockSignals(True)
                a.setChecked(visible)
                a.blockSignals(False)

            # Connect safely
            action.toggled.connect(toggle_dock)
            dock.visibilityChanged.connect(sync_action)

            # Optional: handle icons
            if hasattr(action, "_icon_on") and hasattr(action, "_icon_off") and action._icon_on and action._icon_off:
                def update_icon(checked, act=action):
                    icon = QtGui.QIcon()
                    icon.addPixmap(
                        act._icon_on.pixmap(30, 30) if checked else act._icon_off.pixmap(30, 30)
                    )
                    act.setIcon(icon)

                action.toggled.connect(update_icon)
