"""
Toolbar Builder

This module defines the ToolbarBuilder class, responsible for dynamically creating
toolbars in the Netmig main window. It organizes actions into categorized QToolBars
for quick access to frequent operations like file handling, script execution, and
viewing tools.
"""

import os
from PyQt5 import QtWidgets, QtGui, QtCore


class ToolbarBuilder:
    """
    Constructs QToolBar objects using structured action definitions.

    Toolbars group related actions for quick access in the UI. Each toolbar is
    configured with custom icons and behavior and integrated into the main window.
    """

    TOOLBARS = {
        "Files": ["open_inventory", "open_add_script", "open_sessions", "open_preferences"],
        "Actions": ["open_scripts_folder", "open_outputs_folder", "refresh"],
        "Script Actions": ["abort_script", "set_network_session", "view_code", "view_readme", "run_in_terminal"],
    }

    def __init__(self, mainwindow):
        """
        Initialize the ToolbarBuilder.

        Args:
            mainwindow (QMainWindow): The main application window where the toolbars will be added.
        """
        self.mainwindow = mainwindow
        self.toolbars = {}

    def create_toolbars(self):
        """
        Creates QToolBar instances for each group defined in TOOLBARS.

        Populates each toolbar with the corresponding actions retrieved from
        the main window's `actions` dictionary.

        Returns:
            dict: A dictionary mapping toolbar names to QToolBar objects.
        """
        for name, action_names in self.TOOLBARS.items():
            toolbar = QtWidgets.QToolBar(self.mainwindow)
            toolbar.setObjectName(f"QToolBar:{name}")
            toolbar.setIconSize(QtCore.QSize(30, 30))

            # Add actions to the toolbar
            for action_name in action_names:
                action = self.mainwindow.actions.get(action_name)
                if action:
                    toolbar.addAction(action)

            self.toolbars[name] = toolbar
        return self.toolbars

    def add_to_mainwindow(self):
        """
        Adds all constructed toolbars to the QMainWindow instance.

        Toolbars are docked in the main window based on the layout policy.
        """
        for toolbar in self.toolbars.values():
            self.mainwindow.addToolBar(toolbar)
