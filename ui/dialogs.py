"""
Dialogs

- **SplashScreen**: A dialog that appears when the application is loading, typically displaying
  a logo or progress information.

- **ShowCode**: A dialog for displaying the source code of a script or a file, allowing users
  to review the code in a readable format.

- **ShowReadme**: A dialog to display the README content of a script or tool, providing
  users with helpful information or instructions.

- **ShowAbout**: A dialog displaying information about the application, such as the version,
  copyright, and other relevant details.

- **CheckUpdates**: A dialog for checking if updates are available for the application or
  scripts, and providing users with options to update.

- **Preferences**: A dialog for managing user preferences and settings for the application,
  allowing users to configure various aspects of the tool.

- **NetworkSessionManager**: A dialog that manages network sessions, allowing users to
  view, edit, and organize network session configurations.

- **SetNetworkSession**: A dialog for setting up or configuring a new network session, where
  users can specify session details like IP addresses, credentials, and other network-related
  settings.

- **AddScript**: A dialog for adding new scripts to the application, allowing users to install,
  update, or configure scripts.

- **Inventory**: A dialog for managing and displaying an inventory of installed scripts,
  allowing users to filter, load, update, and uninstall scripts.

Each dialog is implemented as a subclass of `QtWidgets.QDialog` and is designed to provide
a clean and intuitive user experience for interacting with different aspects of the application.
"""
import json
import sys
import os
import re
import uuid
import markdown
import base64
import shutil
import logging
import stat

import textwrap
import functools

from packaging import version
from PyQt5 import QtWidgets, QtGui, QtCore
from requests.packages import target


class SplashScreen(QtWidgets.QDialog):
    """
    SplashScreen displays a frameless, translucent loading dialog
    with the Netmig logo and a message.

    This dialog is typically shown during the application startup process
    to inform the user that the application is loading. It features a logo
    and a dynamic message area that can be updated to provide feedback on
    the current loading process.
    """

    def __init__(self, parent=None):
        """
        Initializes the SplashScreen and configures its UI.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.setup_window()  # Call the new setup_window method
        self._setup_ui()  # Setup the user interface
        self.show()

    def setup_window(self):
        """
        Configures window-specific settings, including:
        - Frameless window
        - Translucent background
        - Object name for the window
        - Window size
        """
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setObjectName('SplashScreen')
        self.resize(300, 400)  # Set the initial size of the window

    def _setup_ui(self):
        """
        Sets up the user interface for the splash screen.

        This includes configuring the layout, loading the logo, and adding
        the message label to the splash screen.
        """
        widget = QtWidgets.QWidget(self)
        widget.setObjectName("SplashContent")

        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)

        # Logo
        logo = QtWidgets.QLabel()
        logo.setObjectName('SplashLogo')
        logo.setFixedSize(160, 140)
        logo.setPixmap(QtGui.QPixmap(
            os.path.join(sys.modules['utils'].PATH_RESOURCES_DIR, 'netmiglogo.png')
        ))
        logo.setScaledContents(True)
        logo.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(logo)

        # Loading message
        self.message = QtWidgets.QLabel('Loading..')
        self.message.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.message)

    def set_message(self, text):
        """
        Updates the message displayed on the splash screen.

        Args:
            text (str): The new message to be displayed.
        """
        self.message.setText(text)


class ShowCode(QtWidgets.QDialog):
    """
    A dialog to display the source code of the currently active script with syntax highlighting.

    Args:
        mainwindow (QMainWindow): Reference to the main application window.
    """

    def __init__(self, mainwindow):
        super().__init__(mainwindow)
        self.mainwindow = mainwindow

        # Configure dialog window
        logging.debug("Initializing ShowCode dialog")
        self.setup_window()  # Move window setup to a separate method

        # Setup UI and load script data
        self.setup_ui()
        self.load_data()
        logging.debug("ShowCode dialog initialized")

    def setup_window(self):
        """
        Configures the window-related settings for the ShowCode dialog:
        - Removes the context help button.
        - Sets the window icon.
        - Sets the object name for the dialog.
        - Resizes the window.
        """
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowType.WindowContextHelpButtonHint)
        self.setWindowIcon(self.mainwindow.icons["code"])
        self.setObjectName("ShowCode")
        self.resize(900, 760)
        logging.debug("ShowCode window setup complete")

    def setup_ui(self):
        """
        Initializes and lays out the text editor widget with syntax highlighting.
        """
        logging.debug("Setting up ShowCode UI")
        self.resize(900, 760)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)

        self.text_edit = QtWidgets.QTextEdit(self)
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)

        # Apply Python syntax highlighter to the text document
        self.code_hightlighter = sys.modules["ui"].PythonSyntaxHighlighter(self.text_edit.document())
        logging.debug("ShowCode UI setup complete")

    def load_data(self):
        """
        Recursively loads all Python files from the current script's directory,
        displaying their content with file headers in the text editor.
        """
        script_name = self.mainwindow.script_orch.curr_script_name
        script_path = self.mainwindow.script_orch.curr_module_path

        if not script_name:
            logging.warning("No script loaded to display source code")
            return

        logging.debug(f"Loading source code for script: {script_name}")
        self.setWindowTitle(f"{script_name} > Code")

        all_code = []
        # Traverse the directory and subdirectories
        for root, _, files in os.walk(self.mainwindow.script_orch.curr_module_path):
            for file in sorted(files):
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            code = f.read()
                            rel_path = os.path.relpath(file_path, script_path)
                            header = f"\n\n# {'=' * 30} {rel_path} {'=' * 30}\n\n"
                            all_code.append(header + code)
                            logging.debug(f"Loaded code from: {rel_path}")
                    except (OSError, IOError) as e:
                        logging.error(f"Error reading {file_path}: {e}")
                        all_code.append(f"\n# Error reading {file_path}:\n# {e}\n")

        self.text_edit.setText("".join(all_code).strip())
        self.show()
        logging.debug("Source code loaded and displayed")


class ShowReadme(QtWidgets.QDialog):
    """
    A dialog that displays the README file of the currently selected script in HTML format.

    This class reads a markdown-formatted README.md file from the script directory,
    converts it to styled HTML, and displays it in a QTextEdit widget. It allows users
    to view the documentation of the active script in a formatted manner.

    Args:
        mainwindow (QMainWindow): The reference to the main application window.
    """

    def __init__(self, mainwindow):
        """
        Initializes the ShowReadme dialog.

        Args:
            mainwindow (QMainWindow): The reference to the main application window,
                                       used to access the current script and its readme.
        """
        super().__init__(mainwindow)
        self.mainwindow = mainwindow

        # Configure window-specific settings
        logging.debug("Initializing ShowReadme dialog")
        self.setup_window()

        # Setup the user interface and load the README content
        self.setup_ui()
        self.load_data()
        logging.debug("ShowReadme dialog initialized")

    def setup_window(self):
        """
        Configures the window-related settings for the ShowReadme dialog.

        - Removes the context help button from the window.
        - Sets the window icon.
        - Sets the object name for the dialog.
        - Resizes the window to a fixed size.

        This method centralizes all window setup-related configurations.
        """
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowType.WindowContextHelpButtonHint)
        self.setWindowIcon(self.mainwindow.icons["about"])
        self.setObjectName("ShowReadme")
        self.resize(900, 760)
        logging.debug("ShowReadme window setup complete")

    def setup_ui(self):
        """
        Sets up the UI layout and components for displaying the README file.

        The layout includes a QTextEdit widget for displaying the styled HTML content of
        the README file. The widget is set to read-only mode to prevent editing.
        """
        logging.debug("Setting up ShowReadme UI")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)

        self.text_edit = QtWidgets.QTextEdit(self)
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        logging.debug("ShowReadme UI setup complete")

    def load_data(self):
        """
        Loads the README file for the active script and displays it in the QTextEdit widget.

        The method retrieves the README file, converts its markdown content into styled HTML,
        and sets it in the QTextEdit widget for display. If an error occurs while reading the file,
        it displays an error message in the widget.

        """
        script_name = self.mainwindow.script_orch.curr_script_name
        readme_path = self.mainwindow.script_orch.curr_script_readme_path

        if not script_name:
            logging.warning("No script loaded to display README")
            return

        # Set the window title based on the current script name
        logging.debug(f"Loading README for script: {script_name}")
        self.setWindowTitle(f"{script_name} > Readme")

        try:
            # Open and read the README file
            with open(self.mainwindow.script_orch.curr_script_readme_path, "r", encoding="utf-8") as file:
                content = file.read()

                # Convert markdown to styled HTML
                styled_html = sys.modules["utils"].md_to_html(content, base_path=os.path.dirname(readme_path))
                # Set the styled HTML content in the text editor
                self.text_edit.setHtml(styled_html)
                self.text_edit.moveCursor(QtGui.QTextCursor.Start)  # Move cursor to the start
                self.show()
                logging.debug("README loaded and displayed successfully")

        except (OSError, IOError) as e:
            # Display error if file cannot be read
            self.text_edit.setText(f"# Error loading readme:\n# {e}")
            logging.error(f"Error loading README from {readme_path}: {e}")


class ShowAbout(QtWidgets.QDialog):
    """
    A dialog that displays information about the Netmig application, including:
    - Name, version, and copyright
    - Project description
    - License
    - Acknowledgements (e.g., PyQt5, Icons8)

    This dialog also sets a custom icon, applies dark titlebar if applicable,
    and displays a status bar message when opened.

    Args:
        mainwindow (QMainWindow): The reference to the main application window, used for retrieving app info.
    """

    def __init__(self, mainwindow):
        """
        Initializes the ShowAbout dialog.

        Args:
            mainwindow (QMainWindow): The reference to the main application window,
                                       used to access the application information.
        """
        super().__init__(mainwindow)
        self.mainwindow = mainwindow
        logging.debug("Initializing ShowAbout dialog.")

        # Configure window-specific settings
        self.setup_window()

        # Setup the user interface
        self.setup_ui()
        logging.debug("ShowAbout dialog initialized and displayed.")

    def setup_window(self):
        """
        Configures the window-related settings for the ShowAbout dialog.

        - Removes the context help button from the window.
        - Sets the object name for the dialog.
        - Adjusts the fixed size of the dialog.

        This method centralizes all window setup-related configurations.
        """
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowType.WindowContextHelpButtonHint)
        self.setObjectName("ShowAbout")
        self.setFixedSize(600, 700)
        logging.debug("ShowAbout window configuration complete.")

    def setup_ui(self):
        """
        Initializes the layout and widgets of the About dialog.

        The layout includes:
        - A top section with the app logo and info.
        - A tab widget containing "About", "License", and "Acknowledgements" tabs.
        - An "OK" button to close the dialog.
        """
        self.setWindowTitle("About")
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        # Setup the top section (logo and app info)
        self._setup_top_widget()

        # Setup the tabs for About, License, and Acknowledgements
        self._setup_tabs()

        # Setup the OK button for closing the dialog
        self._setup_ok_button()

        self.show()
        logging.debug("UI setup for ShowAbout dialog completed.")

    def _setup_top_widget(self):
        """
        Sets up the top section with the application logo and information.

        This section contains the app logo, name, version, copyright, and a link to the project’s Git repository.
        """
        logging.debug("Setting up top widget of ShowAbout dialog.")
        top_layout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(top_layout, stretch=3)
        top_layout.setContentsMargins(10, 10, 10, 10)
        top_layout.setSpacing(50)

        # App logo
        icon_label = QtWidgets.QLabel()
        icon_label.setFixedSize(160, 140)
        icon_label.setPixmap(QtGui.QPixmap(os.path.join(sys.modules["utils"].PATH_RESOURCES_DIR, "netmiglogo.png")))
        icon_label.setScaledContents(True)
        top_layout.addWidget(icon_label)

        # App info
        info_layout = QtWidgets.QVBoxLayout()
        top_layout.addLayout(info_layout)
        info_layout.setContentsMargins(10, 10, 10, 10)
        info_layout.setSpacing(15)

        # Name, version, copyright, and Git link
        name_label = QtWidgets.QLabel(self.mainwindow.cache['app_info']["title"])
        version_label = QtWidgets.QLabel(f"Version {self.mainwindow.cache['app_info']['version']}")
        copyright_label = QtWidgets.QLabel(self.mainwindow.cache['app_info']["copyright"])
        git_url = self.mainwindow.cache['app_info']['git']
        git_link_label = QtWidgets.QLabel(
            f'<a href="{git_url}" style="color:#1a73e8; text-decoration: underline;">{git_url}</a>'
        )
        git_link_label.setOpenExternalLinks(True)

        info_layout.addWidget(name_label)
        info_layout.addWidget(version_label)
        info_layout.addWidget(copyright_label)
        info_layout.addWidget(git_link_label)

        info_layout.addStretch()
        logging.debug("Top widget setup completed.")

    def _setup_tabs(self):
        """
        Sets up the tab widget with three tabs: About, License, and Acknowledgements.

        Each tab contains relevant information, such as the README file for the About tab,
        the license for the License tab, and acknowledgements for external resources in the Acknowledgements tab.
        """
        logging.debug("Setting up tabs in ShowAbout dialog.")
        tab_widget = QtWidgets.QTabWidget()
        self.layout.addWidget(tab_widget, stretch=7)

        # About tab
        about_tab = QtWidgets.QWidget()
        about_layout = QtWidgets.QVBoxLayout(about_tab)
        about_layout.setContentsMargins(5, 5, 5, 5)
        about_text_edit = QtWidgets.QTextEdit(about_tab)
        about_text_edit.setHtml(sys.modules["utils"].md_to_html(self.mainwindow.cache['app_info']['readme']))
        about_layout.addWidget(about_text_edit)
        tab_widget.addTab(about_tab, "About")

        # License tab
        license_tab = QtWidgets.QWidget()
        license_layout = QtWidgets.QVBoxLayout(license_tab)
        license_layout.setContentsMargins(5, 5, 5, 5)
        license_text_edit = QtWidgets.QTextEdit(license_tab)
        license_text_edit.setText(self.mainwindow.cache['app_info']['license'])
        license_layout.addWidget(license_text_edit)
        tab_widget.addTab(license_tab, "License")

        # Acknowledgements tab
        ack_tab = QtWidgets.QWidget()
        ack_layout = QtWidgets.QVBoxLayout(ack_tab)
        ack_layout.setContentsMargins(10, 10, 10, 10)
        ack_layout.setSpacing(10)

        # PyQt5 acknowledgment
        pyqt_layout = QtWidgets.QVBoxLayout()
        pyqt_label = QtWidgets.QLabel("PyQt5 is a cross-platform GUI toolkit, a set of python bindings for Qt v5.")
        pyqt_label.setStyleSheet("font-weight: 300;")
        pyqt_layout.addWidget(pyqt_label)

        pyqt_link = QtWidgets.QLabel(
            '<a href="https://www.riverbankcomputing.com/software/pyqt/" '
            'style="color:#1a73e8; text-decoration:underline;">'
            'https://www.riverbankcomputing.com/software/pyqt/</a>'
        )
        pyqt_link.setOpenExternalLinks(True)
        pyqt_link.setStyleSheet("font-weight: 300;")
        pyqt_layout.addWidget(pyqt_link)

        ack_layout.addLayout(pyqt_layout)

        # Icons8 acknowledgment
        icons_layout = QtWidgets.QVBoxLayout()
        icons_label = QtWidgets.QLabel("Icons courtesy of Icons8")
        icons_label.setStyleSheet("font-weight: 300;")
        icons_layout.addWidget(icons_label)

        icons_link = QtWidgets.QLabel(
            '<a href="https://icons8.com/icons/fluency" '
            'style="color:#1a73e8; text-decoration:underline;">'
            'https://icons8.com/icons/fluency</a>'
        )
        icons_link.setOpenExternalLinks(True)
        icons_link.setStyleSheet("font-weight: 300;")
        icons_layout.addWidget(icons_link)

        ack_layout.addLayout(icons_layout)
        ack_layout.addStretch()

        tab_widget.addTab(ack_tab, "Acknowledgements")
        logging.debug("Tab widget setup complete.")

    def _setup_ok_button(self):
        """
        Adds the OK button to close the dialog.

        This method creates a button that, when clicked, closes the About dialog.
        """
        logging.debug("Setting up OK button for ShowAbout dialog.")
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 10, 0)
        button_layout.addStretch()

        ok_button = QtWidgets.QPushButton("OK")
        ok_button.setMinimumSize(80, 0)
        ok_button.clicked.connect(self.close)
        button_layout.addWidget(ok_button)

        self.layout.addLayout(button_layout)
        logging.debug("OK button added to dialog.")


class CheckUpdates(QtWidgets.QDialog):
    """
    Dialog to check for, download, and apply updates from the Git repository.
    """

    def __init__(self, mainwindow):
        """
        Initializes the CheckUpdates dialog.

        Args:
            mainwindow (QMainWindow): The reference to the main application window.
        """
        super().__init__(mainwindow)
        logging.debug("Initializing CheckUpdates dialog.")
        self.mainwindow = mainwindow
        self.setup_window()
        self.setup_ui()
        self.show()
        self._init_threads()
        self._check_git_version()

    def setup_window(self):
        """Sets up window-specific attributes such as flags, title, and size."""
        logging.debug("Setting up window for CheckUpdates dialog.")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowType.WindowContextHelpButtonHint)
        self.setObjectName("CheckUpdates")
        self.setWindowIcon(self.mainwindow.icons['cloud-sync'])
        self.setWindowTitle('Updates')
        self.setFixedSize(300, 85)

    def setup_ui(self):
        """Initializes the UI layout and widgets."""
        logging.debug("Setting up UI layout and widgets for CheckUpdates.")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        self.text_edit = QtWidgets.QTextEdit()
        layout.addWidget(self.text_edit)
        self.text_edit.setText('Service not running')
        self.text_edit.setReadOnly(True)

        button_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(button_layout)
        button_layout.addItem(
            QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum))

        self.update_button = QtWidgets.QPushButton('Update')
        self.update_button.setMinimumSize(QtCore.QSize(80, 0))
        self.update_button.hide()
        button_layout.addWidget(self.update_button)

        self.restart_button = QtWidgets.QPushButton('Restart')
        self.restart_button.setMinimumSize(QtCore.QSize(80, 0))
        self.restart_button.hide()
        button_layout.addWidget(self.restart_button)

        cancelButton = QtWidgets.QPushButton('Cancel')
        cancelButton.setMinimumSize(QtCore.QSize(80, 0))
        cancelButton.clicked.connect(self.close)
        button_layout.addWidget(cancelButton)

    def _init_threads(self):
        """Prepare thread references for later use."""
        logging.debug("Initializing threads for CheckUpdates.")
        self.threads = {
            'check_version': None,
            'requirements': None,
            'download_repo': None,
            'wait_restart': None
        }

    def _check_git_version(self):
        """Start thread to check the latest version from GitHub."""
        logging.debug("Checking for updates from GitHub.")
        self.text_edit.setText('Checking for updates...')
        git_url = f"{self.mainwindow.cache['app_info']['git']}/blob/master/__app__?raw=true"
        self.threads['check_version'] = sys.modules["ui"].CheckGitVersion(git_url)
        self.threads['check_version'].version_signal.connect(self._on_git_version_received)
        self.threads['check_version'].message_signal.connect(self.text_edit.setText)
        self.threads['check_version'].start()

    def _on_git_version_received(self, git_version):
        """Handles the received git version and displays the appropriate status."""
        logging.debug(f"Received git version: {git_version}")
        local_version = version.parse(self.mainwindow.cache['app_info']["version"])
        remote_version = version.parse(git_version)

        if local_version < remote_version:
            logging.debug(f"New version available: {git_version}")
            self.text_edit.setText(f'New version available (v{git_version})')
            self.update_button.show()
        else:
            logging.debug("No updates found; application is up to date.")
            self.text_edit.setText('Netmig is up to date')

    def _update_action(self):
        """Trigger the update process."""
        logging.debug("Update triggered by user.")
        self.update_button.setDisabled(True)
        self.text_edit.setText("Gathering Python package requirements...")
        self._get_requirements()

    def _get_requirements(self):
        """Fetch updated requirements.txt from the repo."""
        logging.debug("Fetching requirements.txt from GitHub.")
        req_url = f"{self.mainwindow.cache['app_info']['git']}/blob/master/requirements.txt?raw=true"
        self.threads['requirements'] = sys.modules["ui"].GetRequirements(req_url)
        self.threads['requirements'].message_signal.connect(self.text_edit.setText)
        self.threads['requirements'].finished.connect(self._download_repo)
        self.threads['requirements'].start()

    def _download_repo(self):
        """Download and extract the latest repo from GitHub."""
        logging.info("Starting repository download.")
        zip_url = f"{self.mainwindow.cache['app_info']['git']}/zipball/master/"
        self.text_edit.setText("Downloading update...")
        self.threads['download_repo'] = sys.modules["ui"].DownloadRepo(
            zip_url,
            sys.modules["utils"].PATH_GIT_CACHE_DIR,
            sys.modules["utils"].PATH_APP_DIR
        )
        self.threads['download_repo'].success_signal.connect(self._on_download_complete)
        self.threads['download_repo'].start()

    def _on_download_complete(self, status_code):
        """Handle completion of the repository download."""
        logging.debug(f"Download completed with status code: {status_code}")
        if status_code == 200:
            self.text_edit.setText("Download Finished!")
            logging.info("Update download completed successfully.")
            self.update_button.hide()
            self.restart_button.show()
            self._wait_before_restart()
        else:
            logging.warning(f"Download failed with status code {status_code}")
            self.text_edit.setText(f"Download failed with status code {status_code}")

    def _wait_before_restart(self):
        """Wait briefly before offering restart."""
        logging.debug("Waiting briefly before restart.")
        self.threads['wait_restart'] = sys.modules["ui"].WaitRestart()
        self.threads['wait_restart'].message_signal.connect(self.text_edit.setText)
        self.threads['wait_restart'].finished.connect(self._restart)
        self.threads['wait_restart'].start()

    def _restart(self):
        """Restart the application."""
        logging.info("Restarting the application...")
        QtCore.QCoreApplication.quit()
        QtCore.QProcess.startDetached(sys.executable, sys.argv)

    def closeEvent(self, event):
        """Ensure threads are terminated cleanly on close."""
        logging.debug("Closing CheckUpdates dialog and terminating threads.")
        for thread in self.threads.values():
            if thread and thread.isRunning():
                try:
                    thread.terminate()
                    logging.debug(f"Thread {thread} terminated.")
                except Exception as e:
                    logging.warning(f"Failed to terminate thread: {e}")
        super().closeEvent(event)


class Preferences(QtWidgets.QDialog):
    """
    Preferences dialog for configuring general appearance, repository servers, and environment variables.
    This dialog allows the user to set UI preferences, repository server details, and environment variables
    for the application.
    """

    def __init__(self, mainwindow):
        """
        Initialize the Preferences dialog.

        Args:
            mainwindow (QMainWindow): The main window of the application, used to access global settings.
        """
        super().__init__(mainwindow)
        self.mainwindow = mainwindow
        logging.debug("Initializing Preferences dialog.")

        # Setup the window properties and UI elements
        self.setup_window()
        self.setup_ui()
        self._load_data()
        self.show()

    def setup_window(self):
        """
        Configure window-specific settings such as flags, attributes, and window size.
        This method handles visual aspects like window decorations, transparency, and initial size.
        """
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowType.WindowContextHelpButtonHint)
        self.setObjectName("Preferences")
        self.setWindowIcon(self.mainwindow.icons['preferences'])
        self.setWindowTitle('Preferences')
        self.resize(380, 350)
        logging.debug("Preferences window configured.")

    def setup_ui(self):
        """Setup the main layout and tab widget."""
        logging.debug("Setting up UI for Preferences dialog.")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tab_widget = QtWidgets.QTabWidget()
        layout.addWidget(self.tab_widget)

        self._setup_general_tab()
        self._setup_server_tab()
        self._setup_git_tab()

        # Buttons at the bottom
        buttons_widget = QtWidgets.QWidget()
        buttons_layout = QtWidgets.QHBoxLayout(buttons_widget)
        buttons_layout.addStretch()

        self.ok_button = QtWidgets.QPushButton('Ok')
        self.ok_button.clicked.connect(self.close)
        buttons_layout.addWidget(self.ok_button)

        self.cancel_button = QtWidgets.QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.close)
        buttons_layout.addWidget(self.cancel_button)

        self.apply_button = QtWidgets.QPushButton('Apply')
        self.apply_button.clicked.connect(self.apply)
        buttons_layout.addWidget(self.apply_button)

        buttons_layout.addStretch()
        layout.addWidget(buttons_widget)
        logging.debug("UI setup completed.")

    def _setup_general_tab(self):
        """Setup the general appearance settings tab."""
        logging.debug("Configuring 'General' tab in Preferences.")
        general_tab = QtWidgets.QWidget()
        self.tab_widget.addTab(general_tab, 'General')
        layout = QtWidgets.QVBoxLayout(general_tab)

        # Appearance Settings
        appearance_box = QtWidgets.QGroupBox('Appearance')
        layout.addWidget(appearance_box)
        form_layout = QtWidgets.QFormLayout(appearance_box)

        self.style_combobox = QtWidgets.QComboBox()
        self.style_combobox.addItems(map(str.title, QtWidgets.QStyleFactory().keys()))

        self.theme_combobox = QtWidgets.QComboBox()
        self.theme_combobox.addItems(['Light', 'Dark', 'System'])

        self.font_combobox = QtWidgets.QComboBox()
        self.font_combobox.addItems(QtGui.QFontDatabase().families())

        self.point_combobox = QtWidgets.QComboBox()
        self.point_combobox.addItems(map(str, QtGui.QFontDatabase().pointSizes(self.font_combobox.currentText())))

        form_layout.addRow('Style', self.style_combobox)
        form_layout.addRow('Theme', self.theme_combobox)
        form_layout.addRow('Font', self.font_combobox)
        form_layout.addRow('Point', self.point_combobox)

        # Misc Settings
        misc_box = QtWidgets.QGroupBox('Misc.')
        misc_layout = QtWidgets.QGridLayout(misc_box)
        layout.addWidget(misc_box)

        self.load_all_scripts_checkbox = QtWidgets.QCheckBox('Load all scripts at startup')
        misc_layout.addWidget(self.load_all_scripts_checkbox, 0, 0, 1, 3)

        misc_layout.addWidget(QtWidgets.QLabel('Logging level'), 1, 0)
        self.logging_level_combobox = QtWidgets.QComboBox()
        self.logging_level_combobox.addItems(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
        misc_layout.addWidget(self.logging_level_combobox, 1, 1)

        misc_layout.addWidget(QtWidgets.QLabel('Set script output folder'), 2, 0)
        self.set_output_folder_button = QtWidgets.QPushButton('Set Folder')
        self.set_output_folder_button.setMaximumWidth(100)
        self.set_output_folder_button.clicked.connect(self.set_scripts_output_dir)
        misc_layout.addWidget(self.set_output_folder_button, 2, 1)

        misc_layout.addWidget(QtWidgets.QLabel('Scan for scripts'), 3, 0)
        self.scan_scripts_button = QtWidgets.QPushButton('Scan')
        self.scan_scripts_button.setMaximumWidth(100)
        self.scan_scripts_button.clicked.connect(self.scan_scripts)
        misc_layout.addWidget(self.scan_scripts_button, 3, 1)

        misc_layout.addWidget(QtWidgets.QLabel('Reset all data'), 4, 0)
        self.reset_button = QtWidgets.QPushButton('Reset')
        self.reset_button.setMaximumWidth(100)
        self.reset_button.clicked.connect(self.reset_data)
        misc_layout.addWidget(self.reset_button, 4, 1)

    def scan_scripts(self):
        self.mainwindow.scan_scripts()
        logging.info("Scanned scripts...")
        self.mainwindow.app.refresh_ui()

    def reset_data(self):
        reg_path = sys.modules["utils"].PATH_REGISTRIES_TEMPLATES_DIR
        self.mainwindow.settings.update(json.load(open(os.path.join(reg_path, "settings.json"))))
        self.mainwindow.sessions.update(json.load(open(os.path.join(reg_path, "sessions.json"))))
        self.mainwindow.cache.update(json.load(open(os.path.join(reg_path, "cache.json"))))
        logging.info("Reset all data!!")
        self.mainwindow.app.refresh_ui()

    def set_point_size(self, font):
        """
        Update point size combobox based on selected font.

        Args:
            font (QFont): The font selected in the font combobox.
        """
        logging.debug(f"Updating point sizes for selected font: {font.family()}")
        self.point_combobox.clear()
        sizes = QtGui.QFontDatabase().pointSizes(font.family())
        self.point_combobox.addItems(map(str, sizes))

    def _setup_server_tab(self):
        """Setup the SCP server configuration tab."""

        server_tab = QtWidgets.QWidget()
        self.tab_widget.addTab(server_tab, "SCP Server")
        layout = QtWidgets.QVBoxLayout(server_tab)

        connection_box = QtWidgets.QGroupBox('Connection')
        layout.addWidget(connection_box)
        connection_layout = QtWidgets.QFormLayout(connection_box)

        self.server_ip_edit = QtWidgets.QLineEdit()
        self.server_path_edit = QtWidgets.QLineEdit()
        self.server_username_edit = QtWidgets.QLineEdit()
        self.server_password_edit = QtWidgets.QLineEdit()
        self.server_password_edit.setEchoMode(QtWidgets.QLineEdit.Password)

        sync_button = QtWidgets.QPushButton("Sync")
        sync_button.setFixedWidth(100)
        sync_button.clicked.connect(self._sync_scp_server)

        connection_layout.addRow("IP Address", self.server_ip_edit)
        connection_layout.addRow("Path", self.server_path_edit)
        connection_layout.addRow("Username", self.server_username_edit)
        connection_layout.addRow("Password", self.server_password_edit)
        connection_layout.addRow("", sync_button)

        self.server_telemetry = QtWidgets.QCheckBox("Enable telemetry logging")
        layout.addWidget(self.server_telemetry)


        layout.addStretch()

        note_text = 'Use "Netmig AdminTools" to setup and manage the SCP\nserver repository from Admin end.'
        note_label = QtWidgets.QLabel(note_text)
        layout.addWidget(note_label)

        note_link = QtWidgets.QLabel(
            '<a href="https://wwwin-github.cisco.com/sanjeekr/netmig-at" '
            'style="color:#1a73e8; text-decoration:underline;">'
            'https://wwwin-github.cisco.com/sanjeekr/netmig-at</a>'
        )
        note_link.setOpenExternalLinks(True)
        note_link.setStyleSheet("font-weight:300")
        layout.addWidget(note_link)

    def _sync_scp_server(self):
        data = {
            "server": {
                "ip": self.server_ip_edit.text(),
                "path": self.server_path_edit.text(),
                "username": self.server_username_edit.text(),
                "password": self.server_password_edit.text()
            }
        }
        self.mainwindow.settings.update(data)
        self.mainwindow.app.start_scp_sync()

    def _setup_git_tab(self):
        """Setup the Git repos widget."""

        self.git_widget = QtWidgets.QWidget()
        self.tab_widget.addTab(self.git_widget, 'Git Repositories')
        layout = QtWidgets.QVBoxLayout(self.git_widget)

        git_remotes_box = QtWidgets.QGroupBox('URLs')
        layout.addWidget(git_remotes_box)
        git_remotes_layout = QtWidgets.QVBoxLayout(git_remotes_box)
        self.git_remotes_text = QtWidgets.QTextEdit()
        self.git_remotes_text.setFixedHeight(200)
        git_remotes_layout.addWidget(self.git_remotes_text)

        sync_button = QtWidgets.QPushButton("Sync")
        sync_button.setFixedWidth(100)
        sync_button.clicked.connect(self._sync_git)
        git_remotes_layout.addWidget(sync_button)

        layout.addStretch()

    def _sync_git(self):
        data = {
            "git_remotes": self.git_remotes_text.toPlainText().splitlines(),
        }
        self.mainwindow.settings.update(data)
        self.mainwindow.app.start_git_sync()

    def set_scripts_output_dir(self):
        """
        Open a dialog to set the output directory for script files.
        """
        path = QtWidgets.QFileDialog().getExistingDirectory()
        if path:
            self.mainwindow.settings.update({"output_dir": path})
            logging.info(f"Script output directory set to: {path}")

    def _load_data(self):
        """
        Load settings data into the UI elements.
        """
        logging.debug("Loading preferences data into UI.")
        settings_data = self.mainwindow.settings

        self.theme_combobox.setCurrentText(settings_data["styling"]["theme"])
        self.style_combobox.setCurrentText(settings_data["styling"]["style"])
        self.font_combobox.setCurrentText(settings_data["styling"]["font"]["family"])
        self.point_combobox.setCurrentText(str(settings_data["styling"]["font"]["pointSize"]))
        self.logging_level_combobox.setCurrentText(settings_data["logging_level"])
        self.load_all_scripts_checkbox.setChecked(settings_data["load_all_scripts"])
        self.server_telemetry.setChecked(settings_data["telemetry_enabled"])
        self.server_ip_edit.setText(settings_data["server"]["ip"])
        self.server_path_edit.setText(settings_data["server"]["path"])
        self.server_username_edit.setText(settings_data["server"]["username"])
        self.server_password_edit.setText(settings_data["server"]["password"])
        self.git_remotes_text.setText("\n".join(settings_data["git_remotes"]))

        logging.debug("Preferences data loaded successfully.")

    def apply(self):
        """
        Apply the changes made in the preferences dialog.
        """
        logging.info("Applying preferences changes.")

        data = {
            "styling": {
                "theme": self.theme_combobox.currentText(),
                "style": self.style_combobox.currentText(),
                "font": {
                    "family": self.font_combobox.currentText(),
                    "pointSize": int(self.point_combobox.currentText()),
                }
            },
            "logging_level": self.logging_level_combobox.currentText(),
            "load_all_scripts": self.load_all_scripts_checkbox.isChecked(),
            "telemetry_enabled": self.server_telemetry.isChecked(),
            "server": {
                "ip": self.server_ip_edit.text(),
                "path": self.server_path_edit.text(),
                "username": self.server_username_edit.text(),
                "password": self.server_password_edit.text()
            },
            "git_remotes": self.git_remotes_text.toPlainText().splitlines(),
        }
        self.mainwindow.settings.update(data)
        self.mainwindow.app.refresh_ui()
        logging.debug("Preferences updated and UI refreshed.")


class NetworkSessionManager(QtWidgets.QDialog):
    """
    Dialog to manage network sessions. Supports viewing, adding, editing,
    deleting, and saving session details to the application's registries.

    This dialog provides functionalities to manage network session information,
    including jumphost details, network credentials, and default session settings.
    """

    def __init__(self, mainwindow):
        """
        Initializes the NetworkSessionManager dialog.

        Args:
            mainwindow (QtWidgets.QMainWindow): The parent window where this dialog is displayed.
        """
        super().__init__(mainwindow)
        self.mainwindow = mainwindow
        self.current_session_id = None

        logging.debug("Initializing NetworkSessionManager dialog")

        self.setup_window()  # Set up window properties and initial settings
        self.setup_ui()  # Initialize and layout the UI components
        self.load_sessions()  # Load the list of sessions from the main window
        self.show()  # Display the dialog

    def setup_window(self):
        """
        Configures the window properties including flags, attributes, and size.

        This method sets properties like window flags, window context help button
        visibility, object name, and the initial size of the dialog.
        """
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowType.WindowContextHelpButtonHint)
        self.setObjectName("NetworkSessionManager")
        self.resize(750, 560)
        logging.debug("Window setup complete")

    def setup_ui(self):
        """Initializes and lays out all widgets in the dialog."""
        logging.debug("Setting up UI components")
        self.setWindowIcon(self.mainwindow.icons['connection'])
        self.setWindowTitle('Network Session Manager')

        # Layout for the dialog
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Navigation panel layout
        nav_layout = QtWidgets.QVBoxLayout()
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(5)
        layout.addLayout(nav_layout, 3)

        # Filter input for session list
        self.filter_nav = QtWidgets.QLineEdit()
        nav_layout.addWidget(self.filter_nav)
        self.filter_nav.setPlaceholderText("Filter..")
        self.filter_nav.textChanged.connect(self.filter_session_list)

        # Session list widget
        self.session_button_list = QtWidgets.QListWidget()
        self.session_button_list.setContentsMargins(2, 2, 2, 2)
        self.session_button_list.setSpacing(0)
        self.session_button_list.itemClicked.connect(lambda item: self.set_active(item.data(QtCore.Qt.UserRole)))
        nav_layout.addWidget(self.session_button_list)

        # Main form panel layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(2)
        layout.addLayout(main_layout, 7)

        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(5)
        main_layout.addLayout(header_layout)

        # Add session button
        self.add_session_button = QtWidgets.QPushButton()
        self.add_session_button.setToolTip("New Session")
        self.add_session_button.setIcon(self.mainwindow.icons["add-list"])
        self.add_session_button.clicked.connect(self.new_session)
        header_layout.addWidget(self.add_session_button)

        # View raw session data button
        self.view_raw_button = QtWidgets.QPushButton()
        self.view_raw_button.setToolTip("View Session Registry")
        self.view_raw_button.setIcon(self.mainwindow.icons["registry-editor"])
        self.view_raw_button.clicked.connect(
            lambda: sys.modules["utils"].open_path(sys.modules["utils"].PATH_SESSION_DATA))
        header_layout.addWidget(self.view_raw_button)

        # Spacer
        header_layout.addItem(
            QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))

        # Form widget and layout
        self.form_widget = QtWidgets.QWidget()
        main_layout.addWidget(self.form_widget)
        form_layout = QtWidgets.QVBoxLayout(self.form_widget)
        form_layout.setContentsMargins(3, 3, 3, 3)
        form_layout.setSpacing(10)

        # Name input
        name_layout = QtWidgets.QFormLayout()
        name_layout.setContentsMargins(8, 3, 3, 3)
        name_layout.setSpacing(35)
        form_layout.addLayout(name_layout)
        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setFixedWidth(160)
        name_layout.addRow("Name", self.name_edit)

        # Jumphost section
        jumphost_box = QtWidgets.QGroupBox("Jumphost")
        jumphost_layout = QtWidgets.QGridLayout(jumphost_box)
        form_layout.addWidget(jumphost_box)
        self.jumphost_hostname_edit = QtWidgets.QLineEdit()
        self.jumphost_hostname_edit.setFixedWidth(160)
        self.jumphost_username_edit = QtWidgets.QLineEdit()
        self.jumphost_username_edit.setFixedWidth(160)
        jumphost_password = sys.modules["ui"].PasswordField(self.mainwindow.icons)
        self.jumphost_password_edit = jumphost_password.line_edit
        self.jumphost_password_edit.setFixedWidth(160)
        jumphost_layout.addWidget(QtWidgets.QLabel("IP/Host"), 0, 0, 1, 1)
        jumphost_layout.addWidget(self.jumphost_hostname_edit, 0, 1, 1, 1)
        jumphost_layout.addWidget(QtWidgets.QLabel("Username"), 1, 0, 1, 1)
        jumphost_layout.addWidget(self.jumphost_username_edit, 1, 1, 1, 1)
        jumphost_layout.addWidget(QtWidgets.QLabel("Password"), 1, 2, 1, 1)
        jumphost_layout.addWidget(jumphost_password, 1, 3, 1, 2)

        # Network section
        network_box = QtWidgets.QGroupBox("Network")
        network_layout = QtWidgets.QGridLayout(network_box)
        form_layout.addWidget(network_box)
        self.network_username_edit = QtWidgets.QLineEdit()
        self.network_username_edit.setFixedWidth(160)
        network_password = sys.modules["ui"].PasswordField(self.mainwindow.icons)
        self.network_password_edit = network_password.line_edit
        self.network_password_edit.setFixedWidth(160)
        network_layout.addWidget(QtWidgets.QLabel("Username"), 0, 0, 1, 1)
        network_layout.addWidget(self.network_username_edit, 0, 1, 1, 1)
        network_layout.addWidget(QtWidgets.QLabel("Password"), 0, 2, 1, 1)
        network_layout.addWidget(network_password, 0, 3, 1, 2)

        # Default session checkbox
        self.default_checkbox = QtWidgets.QCheckBox("Set as default")
        form_layout.addWidget(self.default_checkbox)

        # Action buttons section
        action_button_widget = QtWidgets.QWidget()
        action_button_widget.setObjectName("NetworkSessionManagerActionWidget")
        action_button_layout = QtWidgets.QHBoxLayout(action_button_widget)
        action_button_layout.setContentsMargins(5, 5, 5, 5)
        action_button_layout.setSpacing(5)
        main_layout.addWidget(action_button_widget)

        # Edit, delete, save, and cancel buttons
        self.edit_button = QtWidgets.QPushButton("Edit")
        self.edit_button.setIcon(self.mainwindow.icons["edit"])
        self.edit_button.clicked.connect(self.edit_session)
        action_button_layout.addWidget(self.edit_button)

        self.delete_button = QtWidgets.QPushButton("Delete")
        self.delete_button.setIcon(self.mainwindow.icons["delete2"])
        self.delete_button.clicked.connect(self.delete_session)
        action_button_layout.addWidget(self.delete_button)

        self.save_button = QtWidgets.QPushButton("Save")
        self.save_button.setIcon(self.mainwindow.icons["save"])
        self.save_button.clicked.connect(self.save_session)
        action_button_layout.addWidget(self.save_button)

        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.setIcon(self.mainwindow.icons["cancel"])
        self.cancel_button.clicked.connect(self.cancel_edit)
        action_button_layout.addWidget(self.cancel_button)

        # Spacer for action buttons
        action_button_layout.addItem(
            QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))

        # Expand main layout
        main_layout.addItem(QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))

        # Initially disable the form widget and set action mode
        self.form_widget.setDisabled(True)
        self.set_action_mode()
        logging.debug("UI setup complete")

    def filter_session_list(self, text):
        """
        Filters the session list based on the text input.

        Args:
            text (str): Text used to filter the session list.
        """
        logging.debug(f"Filtering session list with text: {text}")
        for i in range(self.session_button_list.count()):
            item = self.session_button_list.item(i)
            name = item.text()
            item.setHidden(text.lower() not in name.lower())

    def load_sessions(self):
        """Loads session list into the navigation panel."""
        logging.debug("Loading sessions into navigation panel")
        self.session_button_list.clear()
        for session_id, data in self.mainwindow.sessions.get("sessions").items():
            item = QtWidgets.QListWidgetItem(data["name"])
            item.setData(QtCore.Qt.UserRole, session_id)
            item.setIcon(self.mainwindow.icons["broadcasting"])
            self.session_button_list.addItem(item)

    def set_active(self, session_id):
        """Handles logic when a session is selected from the list."""
        logging.debug(f"Setting active session: {session_id}")
        self.current_session_id = session_id
        session = self.mainwindow.sessions.get("sessions").get(self.current_session_id)
        self.name_edit.setText(session.get("name", ""))
        self.jumphost_hostname_edit.setText(session.get("JUMPHOST_IP", ""))
        self.jumphost_username_edit.setText(session.get("JUMPHOST_USERNAME", ""))
        self.jumphost_password_edit.setText(session.get("JUMPHOST_PASSWORD", ""))
        self.network_username_edit.setText(session.get("NETWORK_USERNAME", ""))
        self.network_password_edit.setText(session.get("NETWORK_PASSWORD", ""))
        self.default_checkbox.setChecked(session.get("default", False))
        self.form_widget.setDisabled(True)
        self.set_action_mode('edit')

    def new_session(self):
        """Clears the form for creating a new session."""
        logging.debug("Creating new session")
        self.current_session_id = None
        self.clear_form()
        self.form_widget.setDisabled(False)
        self.name_edit.setFocus()
        self.set_action_mode('save')

    def edit_session(self):
        """Enables form for editing the selected session."""
        logging.debug(f"Editing session: {self.current_session_id}")
        self.form_widget.setDisabled(False)
        self.set_action_mode('save')

    def save_session(self):
        """Saves the session details to registry (new or update)."""
        if self.name_edit.text():
            is_new = self.current_session_id is None
            session_id = self.current_session_id or str(uuid.uuid4())
            logging.debug(f"{'Creating' if is_new else 'Updating'} session: {session_id}")
            data = {
                "name": self.name_edit.text(),
                "JUMPHOST_IP": self.jumphost_hostname_edit.text(),
                "JUMPHOST_USERNAME": self.jumphost_username_edit.text(),
                "JUMPHOST_PASSWORD": self.jumphost_password_edit.text(),
                "NETWORK_USERNAME": self.network_username_edit.text(),
                "NETWORK_PASSWORD": self.network_password_edit.text(),
                "default": self.default_checkbox.isChecked()
            }
            self.mainwindow.sessions["sessions"][session_id] = data

            if self.default_checkbox.isChecked():
                self.mainwindow.sessions["default_session"] = session_id
                for _session_id, session_info in self.mainwindow.sessions.get("sessions").items():
                    if not session_id == _session_id:
                        self.mainwindow.sessions["sessions"][_session_id]["default"] = False
                for script_id, script_info in self.mainwindow.cache["scripts"].items():
                    self.mainwindow.cache["scripts"][script_id]["session"] = session_id

            self.load_sessions()
            self.form_widget.setDisabled(True)

    def delete_session(self):
        """Deletes the currently selected session from registry."""
        if not self.current_session_id:
            return
        confirm = QtWidgets.QMessageBox.question(
            self, "Delete Session",
            f"Are you sure you want to delete '{self.name_edit.text()}'?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if confirm == QtWidgets.QMessageBox.Yes:
            logging.debug(f"Deleting session: {self.current_session_id}")
            self.mainwindow.sessions["sessions"].pop(self.current_session_id)
            self.current_session_id = None
            self.load_sessions()
            self.clear_form()

    def clear_form(self):
        """Clears all form fields and resets buttons."""
        logging.debug("Clearing form fields")
        self.name_edit.clear()
        self.jumphost_hostname_edit.clear()
        self.jumphost_username_edit.clear()
        self.jumphost_password_edit.clear()
        self.network_username_edit.clear()
        self.network_password_edit.clear()
        self.default_checkbox.setChecked(False)
        self.set_action_mode()

    def cancel_edit(self):
        """Cancels form editing and reloads selected session or clears form."""
        logging.debug("Cancelling edit mode")
        self.form_widget.setDisabled(True)
        if self.current_session_id:
            self.set_active(self.current_session_id)
        else:
            self.clear_form()

    def set_action_mode(self, mode=''):
        """Sets visibility of action buttons based on current mode."""
        logging.debug(f"Setting action mode: {mode}")
        self.edit_button.hide()
        self.delete_button.hide()
        self.save_button.hide()
        self.cancel_button.hide()
        if mode == 'edit':
            self.edit_button.show()
            self.delete_button.show()
        elif mode == 'save':
            self.save_button.show()
            self.cancel_button.show()

    def closeEvent(self, event):
        logging.debug("NetworkSessionManager closed")
        self.mainwindow.app.refresh_ui()
        event.accept()


class SetNetworkSession(QtWidgets.QDialog):
    """
    Dialog for setting a network session to a script. Allows the user to
    view the current session, select a new one from a dropdown, and set or clear
    the session for the current script.
    """

    def __init__(self, mainwindow):
        """
        Initializes the SetNetworkSession dialog.

        Args:
            mainwindow (QtWidgets.QMainWindow): The main window of the application.
        """
        super().__init__(mainwindow)
        self.mainwindow = mainwindow
        logging.debug("Initializing SetNetworkSession dialog.")
        self.setup_window()
        self.setup_ui()
        self.load_data()
        self.show()

    def setup_window(self):
        """
        Configures window-specific settings like window flags, attributes,
        and size.
        """
        self.resize(320, 120)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowType.WindowContextHelpButtonHint)
        self.setObjectName("SetNetworkSession")
        logging.debug("SetNetworkSession window configured.")

    def setup_ui(self):
        """
        Sets up the UI components for the dialog, including labels, combo box, and buttons.
        """
        logging.debug("Setting up UI for SetNetworkSession dialog.")
        self.setWindowIcon(self.mainwindow.icons['broadcasting'])
        self.setWindowTitle('Set Network Session')

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Form Layout for displaying session information
        form_layout = QtWidgets.QFormLayout()
        form_layout.setContentsMargins(5, 5, 5, 5)
        form_layout.setSpacing(12)
        layout.addLayout(form_layout)

        self.name_label = QtWidgets.QLabel()
        self.name_label.setStyleSheet('font-weight: 300')
        form_layout.addRow("Script", self.name_label)

        self.configured_label = QtWidgets.QLabel()
        self.configured_label.setStyleSheet('font-weight: 300')
        form_layout.addRow("Current", self.configured_label)

        self.set_session_combobox = QtWidgets.QComboBox()
        self.set_session_combobox.addItems([session_info.get("name") for session_id, session_info in
                                            self.mainwindow.sessions.get("sessions").items()])
        form_layout.addRow("New", self.set_session_combobox)

        # Button Layout for Set and Clear buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setContentsMargins(5, 5, 5, 5)
        button_layout.setSpacing(10)
        layout.addLayout(button_layout)

        set_button = QtWidgets.QPushButton("Set")
        set_button.setIcon(self.mainwindow.icons['change'])
        set_button.clicked.connect(self.set_config)
        button_layout.addWidget(set_button)

        clear_button = QtWidgets.QPushButton("Clear")
        clear_button.setIcon(self.mainwindow.icons['clear'])
        clear_button.clicked.connect(self.clear_config)
        button_layout.addWidget(clear_button)

    def load_data(self):
        """
        Loads the current script's session information into the dialog.

        Sets the current session name in the label and checks if a session is already set.
        """
        script_name = self.mainwindow.script_orch.curr_script_name
        self.name_label.setText(script_name)
        self.configured_label.setText("Not Set")
        logging.debug(f"Loading session data for script: {script_name}")

        session_id = self.mainwindow.script_orch.curr_script_session
        if session_id:
            session_name = self.mainwindow.sessions.get("sessions")[session_id]["name"]
            self.configured_label.setText(session_name)
            logging.debug(f"Current session set to: {session_name}")

    def set_config(self):
        """
        Sets the selected session for the current script.

        Searches for the selected session by name and updates the script's session
        in the application's cache.

        """
        selected_name = self.set_session_combobox.currentText()
        logging.debug(f"Setting session: {selected_name}")
        for session_id, session_info in self.mainwindow.sessions.get("sessions").items():
            if session_info.get("name") == selected_name:
                self.mainwindow.cache["scripts"][self.mainwindow.script_orch.curr_script_id]["session"] = session_id
                logging.info(
                    f"Session '{selected_name}' set for '{self.mainwindow.script_orch.curr_script_name}'.")
                self.mainwindow.app.refresh_ui()
                self.close()
                return
        logging.warning(f"Selected session name '{selected_name}' not found.")

    def clear_config(self):
        """
        Clears the session for the current script.

        Removes the session from the script's configuration in the application's cache.
        """
        script_id = self.mainwindow.script_orch.curr_script_id
        self.mainwindow.cache["scripts"][script_id].pop("session", None)
        logging.info(f"Session cleared for '{self.mainwindow.script_orch.curr_script_name}'.")
        self.mainwindow.app.refresh_ui()
        self.close()


class AddScript(QtWidgets.QDialog):
    """
    Dialog for adding a new script to the application. This dialog allows
    the user to enter details such as name, module path, version, author,
    tags, readme, and icon, and then creates a new script in the application's
    local script directory.
    """

    def __init__(self, mainwindow):
        """
        Initializes the AddScript dialog.

        Args:
            mainwindow (QtWidgets.QMainWindow): The main window of the application.
        """
        super().__init__(mainwindow)
        self.mainwindow = mainwindow
        logging.debug("Initializing AddScript dialog")
        self.setup_window()
        self.setup_ui()
        self.show()

    def setup_window(self):
        """
        Configures window-specific settings like window flags, attributes,
        and size.
        """
        logging.debug("Setting up AddScript window configuration")
        self.setWindowTitle('Add Script')
        self.setWindowIcon(self.mainwindow.icons['new-file'])
        self.resize(500, 380)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowType.WindowContextHelpButtonHint)
        self.setObjectName("AddScript")

    def setup_ui(self):
        """
        Sets up the UI components for the dialog, including form fields,
        labels, and buttons for script creation.
        """
        logging.debug("Setting up UI components for AddScript dialog")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(30)

        form_layout = QtWidgets.QGridLayout()
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setHorizontalSpacing(5)
        form_layout.setVerticalSpacing(15)

        form_fields = {
            "name": {'icon': 'name', 'mandatory': True, 'placeholder': '__name__', 'type': 'info'},
            "main": {'icon': 'python', 'mandatory': True, 'placeholder': '__main__.py', 'type': 'filepath'},
            "version": {'icon': 'version', 'mandatory': True, 'placeholder': '__version__', 'type': 'info'},
            "author": {'icon': 'writer-male', 'mandatory': False, 'placeholder': '__author__', 'type': 'info'},
            "tags": {'icon': 'tags', 'mandatory': False, 'placeholder': '__tags__', 'type': 'info'},
            "readme": {'icon': 'about', 'mandatory': False, 'placeholder': 'README.md', 'type': 'filepath'},
            "icon": {'icon': 'image', 'mandatory': False, 'placeholder': '__icon__.ico', 'type': 'filepath'}
        }
        self.form_data = {}
        # Adding form fields to the layout
        for row, (name, data) in enumerate(form_fields.items()):
            icon_label = QtWidgets.QLabel()
            icon_label.setPixmap(self.mainwindow.icons[data['icon']].pixmap(20, 20))
            form_layout.addWidget(icon_label, row, 0)

            name_label = QtWidgets.QLabel(name.capitalize() + ':')
            form_layout.addWidget(name_label, row, 1)

            if data['mandatory']:
                mandatory_label = QtWidgets.QLabel("*")
                mandatory_label.setStyleSheet('color:red;')
                form_layout.addWidget(mandatory_label, row, 2)

            text_edit = QtWidgets.QLineEdit()
            text_edit.setPlaceholderText(data['placeholder'])
            form_layout.addWidget(text_edit, row, 3)
            data['text_edit'] = text_edit

            # Adding file path selector for file-type fields
            if data['type'] == 'filepath':
                file_filter = ''
                if match := re.search(r'\.\S+', data['placeholder']):
                    file_filter = f'*{match.group(0)}'

                browse_button = QtWidgets.QPushButton()
                browse_button.setIcon(self.mainwindow.icons['open'])
                browse_button.setObjectName("BrowsePathButton")
                browse_button.clicked.connect(lambda _, te=text_edit, f=file_filter: self.get_path(te, f))
                form_layout.addWidget(browse_button, row, 4)

            self.form_data[name] = data

        layout.addLayout(form_layout)
        layout.addWidget(QtWidgets.QLabel('Fill up the form and click Create'))

        # Create button to trigger script creation
        create_button = QtWidgets.QPushButton("Create")
        create_button.setFixedWidth(150)
        create_button.clicked.connect(self.create_script)
        layout.addWidget(create_button)

    def get_path(self, text_edit, file_filter):
        """
        Opens a file/folder dialog and sets the selected path to the provided
        text_edit widget.

        Args:
            text_edit (QtWidgets.QLineEdit): The text edit widget to display the selected path.
            file_filter (str): The file type filter for the dialog.

        Returns:
            None
        """
        logging.debug(f"Opening file dialog with filter: {file_filter}")
        if file_filter:
            path, _ = QtWidgets.QFileDialog.getOpenFileName(self, filter=file_filter)
        else:
            path = QtWidgets.QFileDialog.getExistingDirectory(self)

        if path:
            logging.debug(f"Selected path: {path}")
            text_edit.setText(path)

    def create_script(self):
        """
        Handles the script creation process based on the form input. The script is created
        by copying the module, readme, and icon files to the appropriate directories, and
        metadata is saved.

        """
        logging.debug("Creating new script from user input")
        scan_data = {}
        # Collect data from form inputs
        for name, data in self.form_data.items():
            scan_data[name] = data['text_edit'].text().strip()

        # Create destination directory and copy the module to it
        logging.debug(f"Collected form data: {scan_data}")

        dir_name = os.path.dirname(scan_data.get("main"))
        main_file = os.path.basename(scan_data.get("main"))

        dest_dir = str(os.path.join(sys.modules["utils"].PATH_SCRIPTS_DIR, str(os.path.basename(dir_name)).lower()))

        logging.debug(f"Copying script module to: {dest_dir}")
        shutil.copytree(dir_name, dest_dir, dirs_exist_ok=True)

        os.rename(os.path.join(dest_dir, main_file), os.path.join(dest_dir, '__main__.py'))

        # Copy the README and icon if provided
        if scan_data.get('readme'):
            shutil.copyfile(scan_data['readme'], os.path.join(dest_dir, 'README.md'))
            logging.debug("README copied")

        if scan_data.get('icon'):
            shutil.copyfile(scan_data['icon'], os.path.join(dest_dir, '__icon__.ico'))
            logging.debug("Icon copied")

        # Generate a unique script ID and save metadata
        script_id = str(uuid.uuid4())
        tags = [tag.strip() for tag in scan_data.get('tags', '').split(',')] if scan_data.get('tags') else []

        meta_data = {
            'name': scan_data['name'],
            'version': scan_data['version'],
            'author': scan_data['author'],
            "uuid": script_id,
            'tags': tags
        }

        logging.debug(f"Saving metadata: {meta_data}")
        meta_file = sys.modules["utils"].PersistentDict(filepath=os.path.join(dest_dir, "__meta__"))
        meta_file.update(meta_data)

        # Update cache and refresh UI
        cache_data = {
            "source": "local",
            "load": True
        }

        self.mainwindow.cache["scripts"][script_id] = cache_data
        logging.info(f"Script {scan_data['name']} added with ID {script_id}")
        self.mainwindow.app.refresh_ui(scan_scripts=True)
        self.close()


class Inventory(QtWidgets.QDialog):
    """
    A dialog to display and manage the inventory of scripts in the application.
    The dialog provides filtering, script details, and actions like install, update, and uninstall.
    """

    def __init__(self, mainwindow):
        """
        Initializes the Inventory dialog.

        Args:
            mainwindow: The main window of the application that manages the icons and cache.
        """
        super().__init__(mainwindow)
        self.mainwindow = mainwindow
        logging.debug("Initializing Inventory dialog.")
        self.setup_window()
        self.setup_ui()
        self.get_scripts()
        self.load_scripts(self.all_scripts)
        self.show()
        logging.debug("Inventory dialog displayed.")

    def setup_window(self):
        """
        Sets up window-specific properties like title, icon, size, and flags.
        """
        logging.debug("Setting up window properties.")
        self.setWindowTitle('Inventory')
        self.setWindowIcon(self.mainwindow.icons['inventory'])
        self.resize(880, 800)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowType.WindowContextHelpButtonHint)
        self.setObjectName("Inventory")

    def setup_ui(self):
        """
        Sets up the UI elements for the Inventory dialog.
        Creates the layout, filter input, and buttons.
        """
        logging.debug("Setting up UI layout and buttons.")
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setSpacing(20)

        top_layout = QtWidgets.QHBoxLayout()
        top_layout.setSpacing(5)
        self.layout.addLayout(top_layout)

        # Filter input for scripts
        self.filter_text = QtWidgets.QLineEdit()
        self.filter_text.setFixedWidth(250)
        self.filter_text.setPlaceholderText("Filter..")
        self.filter_text.textChanged.connect(self.filter_view)
        top_layout.addWidget(self.filter_text)
        top_layout.addSpacing(30)

        # Add Script button
        goto_add_script_button = QtWidgets.QPushButton()
        goto_add_script_button.setIcon(self.mainwindow.icons["new-file"])
        goto_add_script_button.clicked.connect(self.redirect_add_script_)
        top_layout.addWidget(goto_add_script_button)

        # Repo Settings button
        goto_repo_settings_button = QtWidgets.QPushButton()
        goto_repo_settings_button.setIcon(self.mainwindow.icons["repo-settings"])
        goto_repo_settings_button.clicked.connect(self.redirect_repo_setting)
        top_layout.addWidget(goto_repo_settings_button)

        top_layout.addItem(QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Policy.Expanding,
                                                 QtWidgets.QSizePolicy.Policy.Minimum))

        self.setup_scroll_area()

    def setup_scroll_area(self):
        """
        Sets up the scroll area where script cards are displayed.
        """
        logging.debug("Setting up scroll area for script cards.")
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.layout.addWidget(self.scroll_area)
        self.scroll_widget = QtWidgets.QWidget()
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_layout = QtWidgets.QGridLayout(self.scroll_widget)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(15)

    def redirect_add_script_(self):
        """
        Redirects to the Add Script dialog.
        """
        logging.info("Redirecting to Add Script dialog.")
        AddScript(self.mainwindow)

    def redirect_repo_setting(self):
        """
        Redirects to the Repository Settings.
        """
        logging.info("Redirecting to Repository Settings.")
        preferences = Preferences(self.mainwindow)
        preferences.tab_widget.setCurrentIndex(1)

    def filter_view(self, text):
        """
        Filters the displayed scripts based on the provided text.

        Args:
            text: The text to filter the script names.
        """
        logging.debug(f"Filtering scripts with text: {text}")
        self.scroll_area.deleteLater()
        populate_scripts = {}
        for script_id, script_data in self.all_scripts.items():
            if text and not text.lower() in script_data.get("name").lower():
                continue
            populate_scripts[script_id] = script_data
        self.setup_scroll_area()
        self.load_scripts(populate_scripts)

    def load_scripts(self, scripts):
        """
        Loads and displays the scripts in the scroll area.

        Args:
            scripts (dict): A dictionary of consolidated script metadata to display.
        """
        logging.debug(f"Loading {len(scripts)} scripts into the scroll area.")
        row, col, max_col = 0, 0, 3

        for script_id, script_data in scripts.items():
            card = sys.modules["ui"].ScriptCard(self.mainwindow)
            self.scroll_layout.addWidget(card, row, col, 1, 1)

            icon = self.mainwindow.icons.get("python")
            readme_content = "Not available"

            # --- Local script ---
            if script_data.get("source") == "local":
                script_path = str(script_data["module"])
                try:
                    readme_file = os.path.join(script_path, "README.md")
                    if os.path.exists(readme_file):
                        with open(readme_file, "r", encoding="utf-8") as f:
                            readme_content = f.read()
                except Exception as e:
                    logging.warning(f"Could not read README for {script_id}: {e}")

                icon_path = os.path.join(script_path, "__icon__.ico")
                if os.path.exists(icon_path):
                    icon = self.mainwindow.icon_manager.create_icon(icon_path)

                card.badge_icon.setPixmap(self.mainwindow.icons["hdd"].pixmap(20, 20))

            # --- Remote (git or scp) ---
            if script_data.get("source") in ["git", "scp"]:

                if script_data.get("source") == "git":
                    card.badge_icon.setPixmap(self.mainwindow.icons["git"].pixmap(20, 20))
                else:
                    card.badge_icon.setPixmap(self.mainwindow.icons["scp-server"].pixmap(20, 20))

                readme_content = script_data.get("readme", "Not available")
                icon_b64 = script_data.get("icon_data")
                if icon_b64:
                    try:
                        byte_array = QtCore.QByteArray(base64.b64decode(icon_b64))
                        pixmap = QtGui.QPixmap()
                        if pixmap.loadFromData(byte_array):
                            icon = QtGui.QIcon(pixmap)
                    except Exception as e:
                        logging.warning(f"Failed to load icon for {script_id}: {e}")

            # --- Set Script Card Info ---
            card.icon_label.setPixmap(icon.pixmap(50, 50))
            card.name_label.setText(script_data.get("name", "Unnamed Script"))
            tags = script_data.get("tags", [])
            card.tag_label.setText(textwrap.shorten(' | '.join(tags), width=30, placeholder=".."))
            card.readme_text.setText(sys.modules["utils"].md_to_plain(readme_content))

            # --- Script Status Handling ---
            status = script_data.get("status")
            if status == "install":
                card.install_button.clicked.connect(
                    functools.partial(self.install_repo, script_data, card)
                )
                card.install_button.show()

            elif status == "update":
                card.update_button.clicked.connect(
                    functools.partial(self.install_repo, script_data, card)
                )
                card.update_button.setToolTip(
                    f'Update available: v{script_data.get("local_version")} → v{script_data.get("new_version")}'
                )
                card.update_button.show()

            if status in ("installed", "local_only", "update"):
                card.status_label.setText(f"Installed (v{script_data.get('local_version')})")
                card.load_button.clicked.connect(functools.partial(self.load_action, script_id))
                card.load_button.show()

                card.uninstall_button.clicked.connect(
                    functools.partial(self.uninstall_action, script_id, script_data)
                )
                card.uninstall_button.show()

            # --- Layout Grid Positioning ---
            col += 1
            if col >= max_col:
                row += 1
                col = 0

        self.scroll_layout.setRowStretch(row + 1, 1)
        self.scroll_layout.setColumnStretch(max_col, 1)

    def get_scripts(self):
        """
        Consolidates scripts from both local and remote caches into a single dictionary,
        with version tracking and sync status.

        If a script exists in both:
            - Remote data is the base.
            - Adds 'local_version' and 'new_version'.
            - Sets 'status' based on version comparison.

        If only in local:
            - Uses local data.
            - Adds 'local_version' only.
            - Status is 'local_only'.

        If only in remote:
            - Uses remote data.
            - Adds 'new_version' only.
            - Status is 'install'.
        """
        logging.debug("Consolidating scripts with version comparison and sync status.")

        cache = self.mainwindow.cache
        local_scripts = cache.get("scripts", {})
        remote_scripts = cache.get("remote_scripts", {})
        merged_scripts = {}

        all_script_ids = set(local_scripts.keys()) | set(remote_scripts.keys())

        for script_id in all_script_ids:
            local_data = local_scripts.get(script_id)
            remote_data = remote_scripts.get(script_id)

            merged = {}
            local_version = local_data.get("version") if local_data else None
            new_version = remote_data.get("version") if remote_data else None

            # Use remote as base if available, else local
            if remote_data:
                merged.update(remote_data)
            elif local_data:
                merged.update(local_data)

            # Add version fields
            if local_version:
                merged["local_version"] = local_version
            if new_version:
                merged["new_version"] = new_version

            # Determine status
            if local_version and new_version:
                if local_version == new_version:
                    merged["status"] = "installed"
                else:
                    merged["status"] = "update"
            elif new_version:
                merged["status"] = "install"
            else:
                merged["status"] = "local_only"

            merged_scripts[script_id] = merged

        self.all_scripts = merged_scripts

    def load_action(self, script_id):
        """
        Marks the script as loaded and refreshes the UI.

        Args:
            script_id: The ID of the script to load.
        """
        logging.debug(f"Loading script: {script_id}")
        if self.mainwindow.cache["scripts"].get(script_id):
            self.mainwindow.cache["scripts"][script_id]["load"] = True
            self.mainwindow.app.refresh_ui()

    def install_repo(self, script_data, card):
        """
        Initiates the installation or update of a script using either GitInstaller or ScpInstaller
        based on the script's source type. Runs in a background thread to avoid blocking the UI.

        Disables the appropriate button on the associated card and updates the status label
        to show installation progress.

        Args:
            script_data (dict): Script metadata including 'name', 'module', 'source', 'status', etc.
            card (QWidget): The UI card widget representing the script.
        """
        if script_data.get("status") == "install":
            card.install_button.setDisabled(True)
        elif script_data.get("status") == "update":
            card.update_button.setDisabled(True)

        card.status_label.setText(f"Installing {script_data.get('name')}")

        source = script_data.get("source", "")

        if source == "git":
            self.installer_thread = sys.modules["ui"].GitInstaller(script_data)
        elif source == "scp":
            self.installer_thread = sys.modules["ui"].ScpInstaller(script_data, self.mainwindow.settings.get("server"))
        else:
            logging.error(f"Unsupported source type: {source}")
            card.status_label.setText(f"Failed: Unsupported source {source}")
            return

        self.installer_thread.finished.connect(self.on_repo_installed)
        self.installer_thread.start()

    def on_repo_installed(self, success, script_name, error_message):
        """
        Slot triggered when the GitInstaller thread finishes.

        Args:
            success (bool): Indicates whether the installation/update was successful.
            script_name (str): The name of the script.
            error_message (str): Error message if the operation failed.
        """
        if success:
            self.mainwindow.scan_scripts()
            self.get_scripts()
            self.load_scripts(self.all_scripts)
            self.mainwindow.app.refresh_ui()
            logging.info(f"Installation/update completed for {script_name}")
        else:
            QtWidgets.QMessageBox.critical(self, "Git Error", f"Could not install {script_name}\n{error_message}")

    def update_action(self, script_id):
        """
        Initiates the update of the specified script.

        Args:
            script_id: The ID of the script to update.
        """
        logging.debug(f"Updating script: {script_id}")
        pass

    def uninstall_action(self, script_id, script_data):
        """
        Confirms and uninstalls the specified script, removes it from cache,
        and refreshes the UI.

        Args:
            script_id: The ID of the script to uninstall.
            script_data: The metadata of the script to uninstall.
        """
        name = script_data.get("name", "Unnamed Script")

        confirm = QtWidgets.QMessageBox.question(
            self,
            "Inventory",
            f"Uninstall {name}?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )

        if confirm == QtWidgets.QMessageBox.Yes:
            # Remove script folder
            script_path = self.mainwindow.cache["scripts"].get(script_id, {}).get("module", "")
            print(script_path)
            if os.path.isdir(script_path):
                def on_rm_error(func, path, exc_info):
                    os.chmod(path, stat.S_IWRITE)
                    func(path)

                shutil.rmtree(script_path, onerror=on_rm_error)
                logging.debug(f"Deleted script folder: {script_path}")

            # Update main & local registries
            self.mainwindow.cache["scripts"].pop(script_id)
            self.get_scripts()
            self.filter_view("")
            self.load_scripts(self.all_scripts)
            logging.info(f"Uninstalled script '{name}'")

            # Refresh UI
            self.mainwindow.app.refresh_ui()
