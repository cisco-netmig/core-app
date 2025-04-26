"""
Menu Builder

This module defines the MenuBuilder class, responsible for constructing the application's
menu bar in Netmig. It generates structured menus based on a nested dictionary definition,
supports submenus and separators, and links actions from the main window's action registry.
"""

import os
from PyQt5 import QtWidgets, QtGui, QtCore


class MenuBuilder:
    """
    Constructs a hierarchical QMenuBar using a predefined nested dictionary structure.

    Attributes:
        mainwindow (QMainWindow): Reference to the main application window.
        menus (dict): Stores the top-level QMenu instances.
        submenu_icons (dict): Maps submenu names to icons for visual enhancement.
    """

    MENUS = {
        "File": {
            "open_inventory": "Inventory",
            "open_add_script": "Add Script",
            "separator": None,
            "open_preferences": "Preferences",
            "open_sessions": "Sessions",
            "separator_2": None,
            "exit": "Exit"
        },
        "Actions": {
            "Open Path": {
                "open_user_folder": "User Folder",
                "open_scripts_folder": "Scripts Folder",
                "open_outputs_folder": "Outputs Folder"
            },
            "refresh": "Refresh",
            "separator": None,
            "abort_script": "Abort",
            "set_network_session": "Set Network Session",
            "view_code": "View Code",
            "view_readme": "View Readme",
            "run_in_terminal": "Run in Terminal"
        },
        "View": {
            "view_runner": "Runner",
            "view_scripts": "Scripts",
            "view_props": "Properties",
            "view_logger": "Logger",
            "separator": None,
            "reset_view": "Reset View"
        },
        "Help": {
            "Tools": {
                "launch_qtdesigner": "Qt Designer",
                "launch_python_shell": "Python Shell",
                "separator": None
            },
            "separator_2": None,
            "generate_telemetry": "Generate Telemetry",
            "check_updates": "Check for Updates",
            "open_about_netmig": "About Netmig"
        }
    }

    def __init__(self, mainwindow):
        """
        Initialize the MenuBuilder.

        Args:
            mainwindow (QMainWindow): The main application window.
        """
        self.mainwindow = mainwindow
        self.menus = {}
        self.submenu_icons = {
            "Open Path": self.mainwindow.icons.get("opened-folder"),
            "Tools": self.mainwindow.icons.get("tools")
        }

    def create_menus(self):
        """
        Creates top-level QMenus from the MENUS definition.

        Returns:
            dict: A dictionary of QMenu objects keyed by their top-level title.
        """
        for top_menu, items in self.MENUS.items():
            menu = QtWidgets.QMenu(top_menu)
            self._build_menu_items(menu, items)
            self.menus[top_menu] = menu
        return self.menus

    def _build_menu_items(self, menu, items):
        """
        Recursively builds out menu structure, handling actions, submenus, and separators.

        Args:
            menu (QMenu): The parent menu to which items will be added.
            items (dict): Key-value structure representing menu items or nested submenus.
        """
        for key, val in items.items():
            if val is None:
                menu.addSeparator()
            elif isinstance(val, dict):
                sub_menu = QtWidgets.QMenu(key, menu)

                # Apply submenu icon if defined
                icon = self.submenu_icons.get(key)
                if icon:
                    sub_menu.setIcon(icon)

                self._build_menu_items(sub_menu, val)
                menu.addMenu(sub_menu)
            else:
                # Add QAction to menu if it exists in mainwindow.actions
                action = self.mainwindow.actions.get(key)
                if action:
                    action.setText(val)
                    menu.addAction(action)

    def add_to_mainwindow(self):
        """
        Attaches the constructed QMenus to the QMainWindow's menu bar.
        """
        menu_bar = QtWidgets.QMenuBar(self.mainwindow)
        self.mainwindow.setMenuBar(menu_bar)

        # Add each built menu to the menu bar
        for menu in self.menus.values():
            menu_bar.addMenu(menu)
