"""
Docks

1. **LoggerDock**:
   A dockable widget that captures and displays `stdout` and `stderr` messages from running scripts.
   It provides options to filter, search, save, and clear logs, allowing users to track script outputs in real-time.

2. **ScriptsDock**:
   A dockable widget that manages the available scripts for the Netmig application.
   It displays script metadata (such as name, description, version, and status) and allows users to install, update, or
   remove scripts from the system.

3. **PropsDock**:
   A dockable widget that displays static application information, such as the description, version, author, and
   current session details.
   This dock provides users with a quick overview of the current script or session in use.

4. **RunnerDock**:
   A dockable widget that dynamically loads and displays forms for running Python scripts.
   It uses a stacked widget to switch between different script forms, providing a customizable interface for each
   script. The dock widget can load forms, CLI-based interfaces, or error displays based on the script's attributes.

Each of these dockable widgets serves a specific purpose in the Netmig application, allowing users to efficiently
interact with, manage, and monitor scripts and their execution status.

"""

import sys
import re
import os
import logging
import types
import traceback
import logging

from PyQt5 import QtWidgets, QtCore, QtGui


class LoggerDock(QtWidgets.QDockWidget):
    """
    LoggerDock is a dockable widget designed for real-time log capture and display. It supports
    capturing stdout and stderr streams, formatting log messages with different styles for
    various log levels, and providing features such as search, context menu actions, and file
    logging. The widget allows the user to view logs and interact with them via GUI elements.

    """

    def __init__(self, mainwindow):
        """
        Initialize the LoggerDock and set up UI, logging streams, character formatting, and log handlers.

        Args:
            mainwindow (QWidget): The parent widget to which this dockable widget will be attached.
        """
        super().__init__(mainwindow)
        self.mainwindow = mainwindow
        self.setFeatures(
            QtWidgets.QDockWidget.DockWidgetFloatable |
            QtWidgets.QDockWidget.DockWidgetMovable
        )
        self.setWindowTitle('Logger')
        self.setObjectName('LoggerDock')
        self.setMinimumHeight(200)

        # Set the paths for log files
        self.logger_file = sys.modules['utils'].PATH_LOGGER
        self.telemetry_logger_file = sys.modules['utils'].PATH_LOGGER_TELEMETRY

        self.setup_ui()
        self.setup_streams()
        self.setup_char_formats()
        self.setup_loggers()
        self.set_stream()
        self.set_telemetry_logger()

    def setup_ui(self):
        """
        Set up the user interface elements for the logger dock, including the QTextEdit for log
        display and a context menu for user interactions.

        This method initializes the dock widget, creates a layout, and adds a QTextEdit widget
        that will display log messages.
        """
        self.dock_widget = QtWidgets.QWidget()
        self.setWidget(self.dock_widget)

        layout = QtWidgets.QVBoxLayout(self.dock_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.logger_text = QtWidgets.QTextEdit()
        layout.addWidget(self.logger_text)
        self.logger_text.setReadOnly(True)
        self.logger_text_format = self.logger_text.currentCharFormat()
        self.logger_text.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.logger_text.customContextMenuRequested.connect(self.contextMenu)
        logging.debug("Logger UI initialized.")

    def setup_streams(self):
        """
        Set up custom stdout and stderr streams to capture and redirect output to the LoggerDock.

        This method redirects sys.stdout and sys.stderr to custom PyQt streams for capturing
        log messages in real-time. The custom streams are connected to the respective slot functions
        for handling and displaying stdout and stderr messages.
        """
        self.stdout_stream = sys.modules["ui"].StdoutStream()
        self.stdout_stream.text_written.connect(self.write_stdout)
        self.stderror_stream = sys.modules["ui"].StderrStream()
        self.stderror_stream.text_written.connect(self.write_stderr)
        sys.excepthook = self.stderror_stream.excepthook
        logging.debug("Streams connected to custom handlers.")

    def set_stream(self):
        """
        Sets the output stream for logging based on user settings.
        """
        if self.mainwindow.settings.get('logging_stream') == "QStream":
            # Redirect output to custom Qt stream
            sys.stdout = self.stdout_stream
            sys.stderr = self.stderror_stream
            self.stream_handler.setStream(self.stdout_stream)
            logging.debug("Redirecting logs to QStream.")
        else:
            # Restore default system output
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            self.stream_handler.setStream(sys.stdout)
            logging.debug("Restoring default system output.")

    def write_stdout(self, text):
        """
        Handle and format stdout log messages and append them to the logger display.

        Args:
            text (str): The text output from stdout.
        """
        self._append_text(text, log_type='stdout')

    def write_stderr(self, text):
        """
        Handle and format stderr log messages and append them to the logger display.

        Args:
            text (str): The text output from stderr.
        """
        self._append_text(text, log_type='stderr')

    def _append_text(self, text, log_type='stdout'):
        """
        Format and append text to the logger display with appropriate log level coloring.

        Args:
            text (str): The log message.
            log_type (str): The type of log ('stdout' or 'stderr').
        """
        self.logger_text.moveCursor(QtGui.QTextCursor.End)
        self.logger_text.setCurrentCharFormat(self.logger_text_format)

        # Regex to parse structured log lines (timestamp | level | path : [func] message)
        match = re.search(r'^(\S+\s\S+)\s\|\s(\S+)\s\|\s(.+?)\s:\s\[(\S+)\]\s(.*)', text)

        if match:
            # Structured log format
            time_stamp, level_name, path_name, func_name, message = match.groups()
            path_name = os.path.basename(os.path.dirname(path_name)).title()
            func_name = f"SYS.STD:{'Output' if level_name == 'INFO' else 'Error'}" if func_name == "_append_text" else func_name.capitalize()

            # Apply timestamp format
            self.logger_text.setCurrentCharFormat(self.formats.get('TIMESTAMP', self.logger_text_format))
            self.logger_text.insertPlainText(f'{time_stamp} - ')

            # Apply log level format
            self.logger_text.setCurrentCharFormat(self.formats.get(level_name, self.logger_text_format))
            self.logger_text.insertPlainText(level_name)

            # Apply default format for rest of the line
            self.logger_text.setCurrentCharFormat(self.logger_text_format)
            self.logger_text.insertPlainText(f' - {path_name} : [{func_name}] {message}\n')

        else:
            # Non-structured logs (e.g., regular prints or errors)
            if text.strip():
                if log_type == 'stdout':
                    self.logger.info(text)
                else:
                    if text.startswith("Traceback (most recent call last):"):
                        self.logger.error(text.strip())
                    else:
                        self.logger_text.setCurrentCharFormat(self.formats['ERROR'])
                        self.logger_text.insertPlainText(f'{text.strip()}\n')

        self.scroll_logger_to_bottom()

    def scroll_logger_to_bottom(self):
        """
        Scroll the QTextEdit widget to the bottom after the current event loop cycle.

        This ensures the most recent log entry is visible by deferring the scroll until
        the UI has finished processing the current updates.
        """
        QtCore.QTimer.singleShot(0, lambda: self.logger_text.verticalScrollBar().setValue(
            self.logger_text.verticalScrollBar().maximum()
        ))

    def setup_loggers(self):
        """
        Configure the logging system to send output to both the GUI (LoggerDock) and log files.

        This method sets up a logging formatter, creates custom stream and file handlers, and
        attaches them to the main logger. It also defines a custom log level 'SAVINGS' between
        INFO and WARNING.
        """

        logging.addLevelName(15, "SAVINGS")
        setattr(logging.Logger, 'SAVINGS', 15)
        setattr(logging.Logger, 'savings', self.savings_Level)

        self.logger = logging.getLogger()
        self.logger.setLevel(0)

        # 🔥 Clear existing handlers to prevent duplicate output
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        self.formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(pathname)s : [%(funcName)s] %(message)s',
            '%Y-%m-%d %H:%M:%S')

        self.stream_handler = logging.StreamHandler(self.stdout_stream)
        self.stream_handler.setFormatter(self.formatter)
        self.stream_handler.setLevel(15)

        self.file_handler = logging.FileHandler(filename=self.logger_file)
        self.file_handler.setFormatter(self.formatter)
        self.file_handler.setLevel(15)

        self.telemetry_handler = logging.FileHandler(filename=self.telemetry_logger_file)
        self.telemetry_handler.setFormatter(self.formatter)
        self.telemetry_handler.setLevel(15)

        self.logger.addHandler(self.stream_handler)
        self.logger.addHandler(self.file_handler)

        self.suppress_noisy_loggers()

    def suppress_noisy_loggers(self, modules=None, level=logging.ERROR):
        """
        Suppress logging output from specified noisy modules.

        Args:
            modules (list): List of module names to suppress.
            level (int): Minimum logging level to allow (e.g., logging.ERROR).
        """
        if modules is None:
            modules = ["paramiko", "urllib3", "matplotlib", "asyncio", "httpx"]

        for mod in modules:
            mod_logger = logging.getLogger(mod)
            mod_logger.setLevel(level)
            mod_logger.handlers.clear()
            mod_logger.propagate = False

    def set_telemetry_logger(self):
        """
        Configures the telemetry logger based on the application's settings.
        """
        telemetry_enabled = self.mainwindow.settings.get('telemetry_enabled', False)

        if telemetry_enabled:
            self.logger.addHandler(self.telemetry_handler)
            logging.debug("Telemetry logging enabled")
        else:
            self.logger.removeHandler(self.telemetry_handler)
            logging.debug("Telemetry logging disabled")

    def savings_Level(self, message, *args, **kwargs):
        """
        Emit a log message with the custom 'SAVINGS' level (between INFO and WARNING).

        Args:
            message (str): The message to log.
            *args, **kwargs: Additional logging options.
        """
        if self.logger.isEnabledFor(15):
            self.logger._log(15, message, args, **kwargs)

    def setup_char_formats(self):
        """
        Define QTextCharFormat styles for different log levels.

        This method sets up a dictionary of QTextCharFormat instances, each defining a
        specific color for a corresponding log level (e.g., DEBUG, INFO, ERROR).
        """
        self.format_colors = {
            'DEBUG': 'magenta', 'INFO': 'green',
            'WARNING': 'orange', 'ERROR': 'red',
            'CRITICAL': 'darkRed', 'DEFAULT': 'black',
            'TIMESTAMP': '#0081FF', 'SAVINGS': '#C98800'
        }
        self.formats = {}
        for level, color in self.format_colors.items():
            fmt = QtGui.QTextCharFormat()
            fmt.setForeground(QtGui.QColor(color))
            self.formats[level] = fmt

    def save_log(self):
        """
        Open a dialog to allow the user to save the current log contents to a file.

        This method opens a QFileDialog to select the save location and file name, and then writes
        the current contents of the logger display area to the chosen file.
        """
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Log", "log.txt", "Text Files (*.txt)")
        if path:
            with open(path, 'w') as file:
                file.write(self.logger_text.toPlainText())
            logging.info(f"Log saved to {path}")

    def contextMenu(self, pos):
        """
        Show a context menu for the log display when right-clicking, offering options to clear
        or save the log.

        Args:
            pos (QPoint): The position where the context menu was triggered.
        """
        menu = self.logger_text.createStandardContextMenu()
        menu.addSeparator()
        clear_action = QtWidgets.QAction("Clear Log", self)
        clear_action.triggered.connect(self.logger_text.clear)
        save_action = QtWidgets.QAction("Save Log As...", self)
        save_action.triggered.connect(self.save_log)
        menu.addAction(clear_action)
        menu.addAction(save_action)
        menu.exec_(self.logger_text.mapToGlobal(pos))


class ScriptsDock(QtWidgets.QDockWidget):
    """
    A dockable widget for displaying and managing script buttons in the Netmig application.

    This dock provides a scrollable list of toggleable script buttons, each with an optional close button,
    allowing users to interact with available scripts dynamically. It includes a filter to search scripts and
    a close button to unload selected scripts.
    """

    def __init__(self, mainwindow):
        """
        Initializes the ScriptsDock.

        Args:
            mainwindow (QMainWindow): The parent main window, which provides utility icons and script information.
        """
        super().__init__(mainwindow)
        self.mainwindow = mainwindow

        logging.debug("Initializing ScriptsDock...")

        # Set dock properties: floatable and movable
        self.setFeatures(
            QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetFloatable |
            QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetMovable
        )
        self.setWindowTitle('Scripts')
        self.setObjectName('ScriptsDock')
        self.setMinimumHeight(685)

        # Set up the UI and initialize script orchestration
        self.setup_ui()

        logging.debug("ScriptsDock initialized.")

    def setup_ui(self):
        """
        Sets up the user interface for the dock, including a filter line edit and a scroll area
        to hold dynamically added script buttons.

        The filter allows users to search for scripts in the list.
        """
        logging.debug("Setting up UI for ScriptsDock...")

        self.dock_widget = QtWidgets.QWidget()
        self.dock_widget.setFixedWidth(220)
        self.setWidget(self.dock_widget)

        layout = QtWidgets.QVBoxLayout(self.dock_widget)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(5)

        # Filter text input for script searching
        self.filter_nav = QtWidgets.QLineEdit(self)
        layout.addWidget(self.filter_nav)
        self.filter_nav.setPlaceholderText("Filter..")
        self.filter_nav.textChanged.connect(self.filter_script_list)

        # List widget to hold script buttons
        self.script_button_list = QtWidgets.QListWidget()
        layout.addWidget(self.script_button_list)

        logging.debug("UI setup for ScriptsDock complete.")

    def filter_script_list(self, text):
        """
        Filters the script list based on the input text.

        Args:
            text (str): Text used to filter the script list.
        """
        logging.debug(f"Filtering script list with text: '{text}'")

        for i in range(self.script_button_list.count()):
            item = self.script_button_list.item(i)
            widget = self.script_button_list.itemWidget(item)

            if widget:
                # Find the text label inside the custom widget and filter based on the label's text
                text_label = widget.findChild(QtWidgets.QLabel, "script_name_label")
                if text_label:
                    item.setHidden(text.lower() not in text_label.text().lower())

    def add_script(self, script_id, script_info):
        """
        Adds a custom-styled script item to QListWidget with icon, label, and close button.
        The item looks like a cohesive button and is added to the script list.

        Args:
            script_id (str): Unique script identifier.
            script_info (dict): Metadata of the script, should contain 'name' and 'module'.
        """
        logging.debug(f"Adding script to dock: {script_info.get('name')} ({script_id})")

        # Create the list widget item and set size
        item = QtWidgets.QListWidgetItem()
        item.setSizeHint(QtCore.QSize(0, 32))
        item.setData(QtCore.Qt.UserRole, script_id)

        # Create main container widget
        widget = sys.modules["ui"].ScriptListButton()

        icon = self.mainwindow.icons["python"]
        icon_path = os.path.join(script_info.get("module"), '__icon__.ico')
        if os.path.exists(icon_path):
            icon = self.mainwindow.icon_manager.create_icon(icon_path)
        widget.icon_label.setPixmap(icon.pixmap(18, 18))
        widget.text_label.setText(script_info.get("name"))

        # Add to QListWidget
        self.script_button_list.addItem(item)
        self.script_button_list.setItemWidget(item, widget)

        # Connect close button to unload action
        widget.close_button.setIcon(self.mainwindow.icons["close"])
        widget.close_button.clicked.connect(lambda: self.unload_action(script_id))

        # Add mouse press event to set the script as active
        widget.mousePressEvent = lambda event: self.mainwindow.script_orch.set_active(script_id)

    def set_active(self, script_id):
        """
        Updates the visual state of all script widgets to highlight only the selected one.

        Args:
            script_id (str): The unique identifier of the script to mark as active.
        """
        logging.debug(f"Setting active script: {script_id}")

        for i in range(self.script_button_list.count()):
            item = self.script_button_list.item(i)
            widget = self.script_button_list.itemWidget(item)

            if widget:
                is_active = item.data(QtCore.Qt.UserRole) == script_id
                widget.set_active(is_active)

    def unload_action(self, script_id):
        """
        Marks the specified script as unloaded and updates the UI.

        Args:
            script_id (str): The unique identifier of the script to unload.
        """
        logging.debug(f"Unloading script: {script_id}")

        if self.mainwindow.cache["scripts"].get(script_id):
            self.mainwindow.cache["scripts"][script_id]["load"] = False
            self.mainwindow.app.refresh_ui()


class PropsDock(QtWidgets.QDockWidget):
    """
    A dockable widget for displaying static application information such as description,
    version, author, and session details in the Netmig application.
    """

    def __init__(self, mainwindow):
        """
        Initializes the PropsDock.

        Args:
            mainwindow (QMainWindow): The parent main window providing access to utilities and icons.
        """
        super().__init__(mainwindow)
        self.mainwindow = mainwindow

        logging.debug("Initializing PropsDock")
        self.setFeatures(
            QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetFloatable |
            QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetMovable
        )
        self.setWindowTitle('Properties')
        self.setObjectName('PropsDock')
        self.setup_ui()
        logging.debug("PropsDock initialized")

    def setup_ui(self):
        """
        Sets up the user interface for the dock, displaying application metadata including
        description, version, author, and session name.

        The layout includes:
            - Description: A read-only text area displaying the readme or script information.
            - Version: A label displaying the script version.
            - Author: A label displaying the author of the script.
            - Session: A label displaying the current session name.

        Layout includes spacers to align and space elements appropriately.
        """
        logging.debug("Setting up PropsDock UI")

        self.dock_widget = QtWidgets.QWidget()
        self.dock_widget.setFixedWidth(400)
        self.setWidget(self.dock_widget)

        layout = QtWidgets.QVBoxLayout(self.dock_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(1)

        # Description
        layout.addLayout(self._create_header('Description', self.mainwindow.icons["about"]))
        self.readme_text = QtWidgets.QTextEdit()
        self.readme_text.setMinimumHeight(400)
        self.readme_text.setReadOnly(True)
        self.readme_text.setStyleSheet('QTextEdit {padding-left: 22px;} QScrollBar {width: 0px;}')
        self.readme_text.setText('No script loaded!')
        layout.addWidget(self.readme_text)
        layout.addSpacing(20)

        # Version
        layout.addLayout(self._create_header('Version', self.mainwindow.icons["version"]))
        self.version_label = QtWidgets.QLabel()
        self.version_label.setText('No script loaded!')
        self.version_label.setStyleSheet('padding-left: 25px')
        layout.addWidget(self.version_label)
        layout.addSpacing(20)

        # Author
        layout.addLayout(self._create_header('Author', self.mainwindow.icons["writer-male"]))
        self.author_label = QtWidgets.QLabel('Sanjeev Krishna')
        self.author_label.setText('No script loaded!')
        self.author_label.setStyleSheet('padding-left: 25px')
        layout.addWidget(self.author_label)
        layout.addSpacing(20)

        # Session
        layout.addLayout(self._create_header('Session', self.mainwindow.icons["broadcasting"]))
        self.session_label = QtWidgets.QLabel()
        self.session_label.setStyleSheet('padding-left: 25px')
        layout.addWidget(self.session_label)
        layout.addSpacing(20)

        # Spacer to push content to the top
        layout.addItem(
            QtWidgets.QSpacerItem(
                0, 0,
                QtWidgets.QSizePolicy.Policy.Minimum,
                QtWidgets.QSizePolicy.Policy.Expanding
            )
        )
        logging.debug("PropsDock UI setup complete")

    def _create_header(self, text, icon):
        """
        Creates a horizontal layout containing an icon and a label used as section headers.

        Args:
            text (str): The text label for the section.
            icon (QIcon): The icon to be displayed next to the label.

        Returns:
            QHBoxLayout: A layout containing the header icon and label.
        """
        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(10)

        icon_label = QtWidgets.QLabel(self)
        pixmap = icon.pixmap(QtCore.QSize(20, 20))
        icon_label.setPixmap(pixmap)
        layout.addWidget(icon_label)

        text_label = QtWidgets.QLabel(text)
        text_label.setStyleSheet("font-weight: 500;")
        layout.addWidget(text_label)

        # Add spacer to push content to the left
        layout.addItem(
            QtWidgets.QSpacerItem(
                0, 0,
                QtWidgets.QSizePolicy.Policy.Expanding,
                QtWidgets.QSizePolicy.Policy.Minimum
            )
        )
        return layout

    def set_active(self, script_info):
        """
        Updates the properties dock to reflect metadata of the selected script.

        Args:
            script_info (dict): Script metadata. Expected keys: 'name', 'module', 'version', 'author'.
        """
        logging.debug(f"Setting active script in PropsDock: {script_info.get('name', 'Unnamed')}")

        self.readme_text.setText('Not Available')

        readme_path = self.mainwindow.script_orch.curr_script_readme_path
        if os.path.exists(readme_path):
            try:
                with open(readme_path) as f:
                    content = sys.modules["utils"].md_to_plain(f.read())
                    self.readme_text.setText(content)
                    logging.debug(f"Loaded README from: {readme_path}")
            except Exception as e:
                logging.warning(f"Failed to load README from {readme_path}: {e}")

        self.version_label.setText(script_info.get('version', 'Not Available'))
        self.author_label.setText(script_info.get('author', 'Not Available'))

        # Determine and set session name
        session_name = "Not Available"
        sessions = self.mainwindow.sessions.get("sessions")

        if self.mainwindow.script_orch.curr_script_session:
            session = sessions.get(self.mainwindow.script_orch.curr_script_session)
            if session:
                session_name = session.get('name')
        elif self.mainwindow.sessions.get("default_session"):
            self.mainwindow.script_orch.curr_script_session = self.mainwindow.sessions.get("default_session")
            session = sessions.get(self.mainwindow.script_orch.curr_script_session)
            if session:
                session_name = f"{session.get('name')} (default)"

        self.session_label.setText(session_name)
        logging.debug(f"Session label set to: {session_name}")

        logging.debug(f"Active script set in PropsDock: {script_info.get('name', 'Unnamed')}")


class RunnerDock(QtWidgets.QDockWidget):
    """
    A dockable widget used to load and display forms dynamically for running Python scripts
    in the Netmig application. Uses a stacked widget to host multiple script forms.
    """

    def __init__(self, mainwindow):
        """
        Initializes the RunnerDock.

        Args:
            mainwindow (QMainWindow): The main application window, used for accessing utilities
                                       and clearing previously loaded script modules.
        """
        super().__init__(mainwindow)
        self.mainwindow = mainwindow

        logging.debug("Initializing RunnerDock")
        self.setFeatures(QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.setObjectName('RunnerDock')
        self.setupUi()
        logging.debug("RunnerDock initialized")

    def setupUi(self):
        """
        Sets up the user interface by creating and assigning a QStackedWidget as the central widget
        of the dock. Each script form is loaded into a new page in this stack.
        """
        logging.debug("Setting up RunnerDock UI")
        self.form_stack = QtWidgets.QStackedWidget(self)
        setattr(self.form_stack, "map", {})
        self.setWidget(self.form_stack)
        logging.debug("RunnerDock UI setup complete")

    def add_script(self, script_id, script_data):
        """
        Dynamically imports and loads a script form into the dock widget.

        If the script is not a valid module or if form instantiation fails, it falls back to:
        - CliForm: For invalid modules.
        - ErrorForm: For failed form instantiation.

        Args:
            script_id (str): Unique ID of the script.
            script_data (dict): Metadata including 'module' and 'name'.
        """
        module_path = script_data.get('module')
        module_name = os.path.basename(module_path)
        logging.debug(f"Adding script to RunnerDock: {script_data.get('name')} [{script_id}]")

        # Clear previous import if needed
        sys.modules["utils"].clear_modules(module_name)

        try:
            # Attempt to import the module
            module = sys.modules['utils'].import_from_path(module_name, module_path)
            logging.debug(f"Imported module '{module_name}' successfully")
        except Exception as e:
            # If import fails, treat it as a CLI script
            logging.debug(f"Failed to import module '{module_name}': {e}")
            form = sys.modules["ui"].CliForm(self.mainwindow)
        else:
            try:
                # Get session data if available for script_id or use default session if set
                session = script_data.get("session")
                if not session and self.mainwindow.sessions.get("default_session"):
                    session = self.mainwindow.sessions.get("default_session")

                session_data = {}
                if session:
                    session_data = self.mainwindow.sessions["sessions"].get(session).copy()
                    session_data["JUMPHOST_PASSWORD"] = self.mainwindow.cipher.decrypt(
                        session_data.get("JUMPHOST_PASSWORD", ""))
                    session_data["NETWORK_PASSWORD"] = self.mainwindow.cipher.decrypt(
                        session_data.get("NETWORK_PASSWORD", ""))

                # If module has a Form attribute, instantiate it
                if hasattr(module, 'Form') and isinstance(module.Form, (type, types.FunctionType)):
                    kwargs = {
                        "parent": self.form_stack,
                        "icons": self.mainwindow.icons,
                        "script": script_id,
                        "output_dir": self.mainwindow.settings.get("output_dir"),
                        "session": session_data
                    }
                    form = module.Form(**kwargs)
                    logging.debug(f"Form created for script: {script_data.get('name')}")
                else:
                    # No Form class defined, fallback to CLI
                    logging.debug(f"No valid Form found in module '{module_name}', falling back to CLI form")
                    form = sys.modules["ui"].CliForm(self.mainwindow)
            except Exception as e:
                # If Form fails to initialize, show ErrorForm with traceback
                logging.debug(f"Failed to instantiate Form for '{module_name}': {e}")
                form = sys.modules["ui"].ErrorForm(self.mainwindow)
                form.set_error(
                    header=f"Failed to load '{script_data.get('name')}'",
                    message=traceback.format_exc()
                )

        # Add the resolved form to the stack
        self.form_stack.addWidget(form)
        self.form_stack.map[script_id] = {
            "name": script_data.get("name"),
            "form": form
        }
        logging.debug(f"Script form added to stack: {script_data.get('name')} [{script_id}]")

    def set_active(self, script_id):
        """
        Sets the active form in the stacked widget based on the provided script ID.

        Args:
            script_id (str): Unique ID of the script whose form should be displayed.
        """
        name = self.form_stack.map.get(script_id, {}).get("name")
        form = self.form_stack.map.get(script_id, {}).get("form")
        self.setWindowTitle(name)
        self.form_stack.setCurrentWidget(form)
        logging.debug(f"Active script set in RunnerDock: {name} [{script_id}]")
