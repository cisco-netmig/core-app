"""
IconManager

This module provides the IconManager class, which is responsible for loading and managing icon assets 
used throughout the PyQt5 application. It reads all `.ico` files from a specified directory and 
returns them as QIcon objects for use in the UI.

"""

import os
import sys
from PyQt5 import QtWidgets, QtGui, QtCore

class IconManager:
    """
    Manages loading and creating QIcon objects from a specified icon directory.

    Attributes:
        icons_dir (str): Directory path where icon files (.ico) are stored.
    """

    def __init__(self):
        """
        Initializes the IconManager by setting the icon directory path from a module named 'paths'.
        """
        self.icons_dir = sys.modules["utils"].PATH_ICONS_DIR

    def load_icons(self):
        """
        Loads all .ico files from the icon directory into a dictionary.

        Returns:
            dict: A dictionary mapping icon names (without extension) to QtGui.QIcon objects.
        """
        icons = {}

        # Iterate over files in the icon directory
        for file in os.listdir(self.icons_dir):
            if file.endswith(".ico"):
                name = os.path.splitext(file)[0]  # Strip file extension for key
                path = os.path.join(self.icons_dir, file)
                icons[name] = self.create_icon(path)

        return icons

    def create_icon(self, path):
        """
        Creates a QIcon object from a given file path.

        Args:
            path (str): The full file path to the icon.

        Returns:
            QtGui.QIcon: The created icon object, empty if the file does not exist.
        """
        icon = QtGui.QIcon()
        if os.path.exists(path):
            icon.addPixmap(QtGui.QPixmap(path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        return icon
