"""
Widgets

Classes:
    - ScriptCard: A QFrame-based widget that visually represents an individual script entry
      with metadata, status indicators, and actionable buttons (install, update, etc.).

    - PasswordField: A custom QLineEdit subclass that supports toggling password visibility
      with a built-in eye icon.

    - ErrorForm: A simple, styled QWidget used to display formatted error messages or
      exceptions in the application.

    - CliForm: A terminal-like input/output form that allows users to run and interact with
      CLI-based Python scripts within the GUI.

    - ScriptExecutor: A utility class (not a QWidget) used to launch and manage external
      terminal sessions for script execution.

    - PythonSyntaxHighlighter: A QSyntaxHighlighter subclass that applies basic Python syntax
      highlighting to QTextEdit fields, useful for displaying code or README content.

"""

from PyQt5 import QtWidgets, QtGui, QtCore

import re
import sys
import subprocess
import logging
import os
import json
import shlex
import platform
import datetime


import re
from PyQt5 import QtGui

class PythonSyntaxHighlighter(QtGui.QSyntaxHighlighter):
    """
    A QSyntaxHighlighter subclass that provides syntax highlighting for Python code.

    Features:
        - Keywords (e.g., def, class, return)
        - Built-in functions (e.g., print, len)
        - Strings (single and double quotes)
        - Numbers (integers and floats)
        - Comments (lines starting with #)
        - Function names (after 'def')
        - Class names (after 'class')
        - Single-line and multi-line docstrings
    """

    def __init__(self, parent):
        """
        Initialize the syntax highlighter with predefined rules and styles.

        Args:
            parent: A QTextDocument or QTextEdit instance to apply syntax highlighting to.
        """
        super().__init__(parent)

        # Define syntax highlighting rules with regex patterns and colors
        self.rules = {
            "keywords": {
                "pattern": r"\b(def|class|import|from|return|if|elif|else|for|while|try|except|finally|with|as|"
                           r"pass|break|continue|lambda|in|not|is|and|or|async|await|yield|del|assert|global|"
                           r"nonlocal|raise)\b",
                "color": "#005cc5"  # Vibrant blue
            },
            "builtins": {
                "pattern": r"\b(print|len|range|int|str|float|list|dict|set|tuple|open|input|abs|sum|max|min|"
                           r"round|sorted|zip|map|filter|enumerate|chr|ord|hex|bin|bool|dir)\b(?=\()",
                "color": "#d73a49"  # Rich red
            },
            "strings": {
                "pattern": r"(\"[^\"]*\"|'[^']*')",
                "color": "#032f62"  # Deep navy
            },
            "numbers": {
                "pattern": r"\b\d+(\.\d+)?\b",
                "color": "#e36209"  # Orange
            },
            "comments": {
                "pattern": r"#.*",
                "color": "#6a737d"  # Medium gray
            },
            "functions": {
                "pattern": r"\bdef\s+([a-zA-Z_][a-zA-Z0-9_]*)",
                "color": "#22863a",  # Green
                "group": 1
            },
            "classes": {
                "pattern": r"\bclass\s+([A-Z][a-zA-Z0-9_]*)",
                "color": "#6f42c1",  # Purple
                "group": 1
            }
        }

        # Define formatting style for docstrings (multi-line triple-quoted strings)
        self.docstring_format = QtGui.QTextCharFormat()
        self.docstring_format.setForeground(QtGui.QColor("#B58900"))

        self.current_delimiter = None  # Stores which triple-quote is currently active for multiline docstrings

    def highlightBlock(self, text):
        """
        Applies syntax highlighting to a single block (line) of text.

        This includes support for multi-line docstrings using block states,
        and applies predefined regex rules for Python syntax elements.

        Args:
            text (str): The current text block to highlight.
        """
        self.setCurrentBlockState(0)

        # Handle continuation of multi-line docstrings from the previous block
        if self.previousBlockState() == 1:
            end = text.find('"""')
            if end == -1:
                self.setFormat(0, len(text), self.docstring_format)
                self.setCurrentBlockState(1)
                return
            else:
                self.setFormat(0, end + 3, self.docstring_format)
                return

        if self.previousBlockState() == 2:
            end = text.find("'''")
            if end == -1:
                self.setFormat(0, len(text), self.docstring_format)
                self.setCurrentBlockState(2)
                return
            else:
                self.setFormat(0, end + 3, self.docstring_format)
                return

        # Start of a new multi-line docstring
        for delim, state in [('"""', 1), ("'''", 2)]:
            start = text.find(delim)
            if start != -1:
                end = text.find(delim, start + 3)
                if end == -1:
                    self.setFormat(start, len(text) - start, self.docstring_format)
                    self.setCurrentBlockState(state)
                    return
                else:
                    self.setFormat(start, end + 3 - start, self.docstring_format)

        # Highlight single-line triple-quoted docstrings
        for match in re.finditer(r'(\'\'\'[^\'\\]*(?:\\.[^\'\\]*)*\'\'\'|"""[^"\\]*(?:\\.[^"\\]*)*""")', text):
            start, end = match.span()
            self.setFormat(start, end - start, self.docstring_format)

        # Apply regular syntax highlighting rules
        for rule in self.rules.values():
            pattern = re.compile(rule["pattern"])
            fmt = QtGui.QTextCharFormat()
            fmt.setForeground(QtGui.QColor(rule["color"]))

            for match in pattern.finditer(text):
                group_index = rule.get("group", 0)
                start, end = match.span(group_index)
                self.setFormat(start, end - start, fmt)


class PasswordField(QtWidgets.QWidget):
    """
    A custom password input widget that includes a masked QLineEdit and a toggle button
    to show or hide the password.
    """

    def __init__(self, icons, parent=None):
        """
        Initializes the PasswordField widget.

        Args:
            icons (dict): Dictionary of QIcons with 'visible' and 'invisible' keys.
            parent (QWidget, optional): Parent widget.
        """
        super().__init__(parent)
        self.icons = icons
        self._setup_ui()

    def _setup_ui(self):
        """
        Sets up the layout with the QLineEdit and toggle button.
        """
        self.line_edit = QtWidgets.QLineEdit()
        self.line_edit.setEchoMode(QtWidgets.QLineEdit.Password)

        self.toggle_button = QtWidgets.QPushButton()
        self.toggle_button.setCheckable(True)
        self.toggle_button.setToolTip("Show/Hide Password")
        self.toggle_button.setFocusPolicy(QtCore.Qt.NoFocus)

        # Compose toggle icon with state-aware icons
        self.toggle_icon = QtGui.QIcon(self.icons['invisible'])
        self.toggle_icon.addPixmap(
            self.icons['visible'].pixmap(20, 20),
            QtGui.QIcon.Normal,
            QtGui.QIcon.On
        )
        self.toggle_button.setIcon(self.toggle_icon)
        self.toggle_button.setIconSize(QtCore.QSize(20, 20))
        self.toggle_button.toggled.connect(self._toggle_echo)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.toggle_button)

    def _toggle_echo(self, checked):
        """
        Toggles the echo mode of the QLineEdit.
        """
        self.line_edit.setEchoMode(QtWidgets.QLineEdit.Normal if checked else QtWidgets.QLineEdit.Password)

    def text(self):
        """Returns the text from the line edit."""
        return self.line_edit.text()

    def setText(self, value):
        """Sets the text in the line edit."""
        self.line_edit.setText(value)

    def clear(self):
        """Clears the line edit."""
        self.line_edit.clear()

    def setEchoMode(self, mode):
        """Optional: Set echo mode manually."""
        self.line_edit.setEchoMode(mode)

    def lineEdit(self):
        """Returns the inner QLineEdit for advanced access if needed."""
        return self.line_edit


class ScriptListButton(QtWidgets.QWidget):
    """
    A custom QWidget representing a script entry in a list.

    Includes an icon, text label, and a close button. Supports focus-based
    styling changes to visually distinguish active and inactive states.
    """

    def __init__(self):
        """
        Initializes the script list button widget.
        """
        super().__init__()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)

        self.active = False

        self.setup_ui()
        self.set_default_style()

    def setup_ui(self):
        """
        Sets up the UI layout with icon, label, and close button.
        """
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(6)

        # Icon label
        self.icon_label = QtWidgets.QLabel()
        layout.addWidget(self.icon_label)

        # Script name label
        self.text_label = QtWidgets.QLabel()
        self.text_label.setObjectName("script_name_label")
        layout.addWidget(self.text_label)

        layout.addStretch()

        # Close button to unload script
        self.close_button = QtWidgets.QPushButton()
        self.close_button.setFixedSize(20, 20)
        self.close_button.setStyleSheet("""
            QPushButton {
                border-radius: 10px;
                background-color: none;
                text-align: center;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: #88c9d4;
            }
        """)
        layout.addWidget(self.close_button)

    def set_active(self, active: bool):
        """
        Update active state and apply corresponding style.
        """
        self.active = active
        if self.active:
            self.set_active_style()
        else:
            self.set_default_style()

    def set_default_style(self):
        """
        Applies the default (unfocused) style to the widget.
        """
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border-radius: 3px;
                border: none; 
            }
            QWidget:hover {
                background-color: rgba(80, 232, 255, 50);
                border: none; 
            }
            QLabel {
                background-color: none;   
            }
            QLabel:hover {
                background-color: none;   
            }
        """)

    def set_active_style(self):
        """
        Applies the focused (active) style to the widget.
        """
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(80, 232, 255, 50);
                border-radius: 3px;
                border: none; 
            }
            QWidget:hover {
                background-color: rgba(80, 232, 255, 50);
                border: none; 
            }
            QLabel {
                background-color: none;   
            }
            QLabel:hover {
                background-color: none;   
            }
        """)


class ScriptExecutor(QtCore.QObject):
    """
    A QObject-based class to execute a Python script module in a new terminal window.
    Supports Windows, macOS, and Linux.
    """

    def __init__(self, mainwindow, parent=None):
        super().__init__(parent)
        self.mainwindow = mainwindow

    def execute(self):
        """
        Launches the current script in a new terminal window using platform-specific commands.
        """
        path = self.mainwindow.script_orch.curr_module_path

        session = self.mainwindow.script_orch.curr_script_session
        if not session and self.mainwindow.sessions.get("default_session"):
            session = self.mainwindow.sessions.get("default_session")

        session_data = {}
        if session:
            session_data = self.mainwindow.sessions["sessions"].get(session).copy()
            session_data["JUMPHOST_PASSWORD"] = self.mainwindow.cipher.decrypt(
                session_data.get("JUMPHOST_PASSWORD", ""))
            session_data["NETWORK_PASSWORD"] = self.mainwindow.cipher.decrypt(
                session_data.get("NETWORK_PASSWORD", ""))


        if not path:
            logging.warning("No script loaded!")
            return

        if not os.path.exists(path):
            logging.error(f"Could not find: {path}")
            return


        args = [
            sys.executable,
            "-m",
            os.path.basename(path),
            "--lib", json.dumps(sys.path),
            "--output", os.environ.get("NETMIG_OUTPUT_DIR", ""),
            "--session", json.dumps(session_data),
            "--qss", self.mainwindow.app.styleSheet(),
            "--style", json.dumps(self.mainwindow.settings.get('styling'))
        ]

        command = " ".join(shlex.quote(arg) for arg in args)
        cwd = os.path.dirname(path)

        try:
            system = platform.system()

            if system == "Windows":
                logging.info("Launching script in Windows terminal.")
                subprocess.Popen(
                    args,
                    cwd=cwd,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )

            elif system == "Darwin":  # macOS
                logging.info("Launching script in macOS terminal.")
                apple_script = f'''
                tell application "Terminal"
                    do script "cd {shlex.quote(cwd)} && {command}"
                    activate
                end tell
                '''
                subprocess.Popen(["osascript", "-e", apple_script])

            elif system == "Linux":
                logging.info("Launching script in Linux terminal.")
                terminal_cmds = [
                    ["gnome-terminal", "--", "bash", "-c", f"cd {shlex.quote(cwd)} && {command}; exec bash"],
                    ["x-terminal-emulator", "-e", f"bash -c 'cd {shlex.quote(cwd)} && {command}; exec bash'"],
                    ["xterm", "-e", f"cd {shlex.quote(cwd)} && {command}; bash"]
                ]
                for terminal_cmd in terminal_cmds:
                    try:
                        subprocess.Popen(terminal_cmd)
                        break
                    except FileNotFoundError:
                        continue
                else:
                    logging.error("No supported terminal emulator found.")

            else:
                logging.error(f"Unsupported OS: {system}")

        except Exception as e:
            logging.exception("Failed to execute script.")


class ScriptCard(QtWidgets.QFrame):
    """
    A custom PyQt5 widget that displays detailed information about a script,
    including icon, name, tags, README content, status, and action buttons.

    This widget is used in the inventory dialog to present scripts in a card format,
    with support for different actions like loading, installing, updating, and uninstalling.
    """

    def __init__(self, mainwindow):
        """
        Initialize the ScriptCard widget.

        Args:
            mainwindow (QMainWindow): Reference to the main window.
        """
        super().__init__(mainwindow)
        self.mainwindow = mainwindow
        self.setObjectName("ScriptCard")
        self.setup_ui()

    def setup_ui(self):
        """
        Sets up the UI components and layout of the ScriptCard widget.
        """
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setSpacing(5)

        # Header Section
        top_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(top_layout)
        top_layout.setSpacing(10)

        # Icon
        icon_container = QtWidgets.QFrame()
        top_layout.addWidget(icon_container)
        icon_container.setFixedSize(50, 50)
        icon_container.setStyleSheet("position: relative;")
        icon_layout = QtWidgets.QStackedLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        self.icon_label = QtWidgets.QLabel()
        self.icon_label.setFixedSize(50, 50)
        self.icon_label.setScaledContents(True)
        icon_layout.addWidget(self.icon_label)

        # Badge icon (secondary overlay icon)
        self.badge_icon = QtWidgets.QLabel(icon_container)
        self.badge_icon.setFixedSize(20, 20)
        self.badge_icon.setScaledContents(True)
        self.badge_icon.setStyleSheet("background: transparent; position: absolute; right: 0px;bottom: 0px;")
        self.badge_icon.move(30, 30)
        self.badge_icon.raise_()

        # Name and Tag
        info_layout = QtWidgets.QVBoxLayout()
        top_layout.addLayout(info_layout)
        info_layout.setContentsMargins(0, 6, 0, 6)
        info_layout.setSpacing(1)

        self.name_label = QtWidgets.QLabel()
        self.name_label.setStyleSheet('font-size: 12pt; font-weight:400')
        info_layout.addWidget(self.name_label)

        self.tag_label = QtWidgets.QLabel()
        self.tag_label.setStyleSheet('font-size: 8pt; font-weight:400')
        info_layout.addWidget(self.tag_label)

        # README Viewer
        self.readme_text = QtWidgets.QTextEdit()
        self.readme_text.setFixedSize(250, 220)
        self.readme_text.setReadOnly(True)
        layout.addWidget(self.readme_text)

        # Status and Action Buttons
        action_layout = QtWidgets.QHBoxLayout()
        action_layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(action_layout)

        self.status_label = QtWidgets.QLabel()
        action_layout.addWidget(self.status_label)
        action_layout.addStretch()

        self.load_button = QtWidgets.QPushButton()
        self.load_button.setIcon(self.mainwindow.icons["insert"])
        self.load_button.setToolTip("Load script into runner")
        self.load_button.hide()
        action_layout.addWidget(self.load_button)

        self.install_button = QtWidgets.QPushButton()
        self.install_button.setIcon(self.mainwindow.icons["download"])
        self.install_button.setToolTip("Download script")
        self.install_button.hide()
        action_layout.addWidget(self.install_button)

        self.update_button = QtWidgets.QPushButton()
        self.update_button.setIcon(self.mainwindow.icons["update"])
        self.update_button.setToolTip("Update script")
        self.update_button.hide()
        action_layout.addWidget(self.update_button)

        self.uninstall_button = QtWidgets.QPushButton()
        self.uninstall_button.setIcon(self.mainwindow.icons["delete"])
        self.uninstall_button.setToolTip("Uninstall script")
        self.uninstall_button.hide()
        action_layout.addWidget(self.uninstall_button)


class ErrorForm(QtWidgets.QWidget):
    """
    A simple widget for displaying an error message with a header and body.
    """

    def __init__(self, mainwindow):
        """
        Initializes the error form with a vertical layout, including
        a header label, a body label, and a spacer to push content to the top.
        """
        super().__init__(mainwindow)
        self.mainwindow = mainwindow
        self.setup_ui()

    def setup_ui(self):
        """
        Sets up the error message layout with header and body labels.
        """
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setAlignment(QtCore.Qt.AlignTop)

        # Header label
        self.header_label = QtWidgets.QLabel("Error")
        self.header_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(self.header_label)

        # Body text
        self.body_label = QtWidgets.QLabel("An unexpected error occurred.")
        self.body_label.setWordWrap(True)
        self.body_label.setStyleSheet("font-size: 10pt;")
        layout.addWidget(self.body_label)

        # Spacer to push content to top
        layout.addItem(QtWidgets.QSpacerItem(
            0, 0,
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Expanding
        ))

    def set_error(self, header: str, message: str):
        """
        Updates the error form with a custom header and message.

        Args:
            header (str): The title or heading of the error.
            message (str): The detailed error message.
        """
        self.header_label.setText(header)
        self.body_label.setText(message)


class CliForm(QtWidgets.QWidget):
    """
    A widget to execute and interact with CLI-based Python scripts
    via a QTextEdit terminal-like interface.
    """

    def __init__(self, mainwindow):
        super().__init__(mainwindow)
        self.mainwindow = mainwindow
        self.setObjectName("CliForm")
        self.process = QtCore.QProcess(self)

        self.setup_ui()
        self.set_banner()

        self.process.readyReadStandardOutput.connect(self.read_output)

    def setup_ui(self):
        """
        Sets up the user interface elements: buttons, output area, and status label.
        """
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Button Bar
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(3, 3, 3, 3)

        run_button = QtWidgets.QPushButton("Run", parent=self)
        run_button.setIcon(self.mainwindow.icons['run-command'])
        run_button.clicked.connect(self.start_process)
        button_layout.addWidget(run_button)

        abort_button = QtWidgets.QPushButton("Abort", parent=self)
        abort_button.setIcon(self.mainwindow.icons['Esc'])
        abort_button.setIconSize(QtCore.QSize(20, 20))
        abort_button.clicked.connect(self.abort_process)
        button_layout.addWidget(abort_button)

        button_layout.addItem(
            QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        layout.addLayout(button_layout)

        # Terminal Text Edit
        self.text_edit = QtWidgets.QTextEdit(self)
        self.text_edit.installEventFilter(self)
        self.default_format = self.text_edit.currentCharFormat()
        layout.addWidget(self.text_edit)

        # Status Label
        self.status_label = QtWidgets.QLabel("Ready..", parent=self)
        layout.addWidget(self.status_label)

    def start_process(self):
        """
        Starts the Python subprocess to run the selected script.
        """
        self.line_start = len(self.banner_text) - 1
        python_exec = sys.executable.replace("pythonw.exe", "python.exe")
        script_path = self.mainwindow.script_orch.curr_module_path

        self.process.start(f"\"{python_exec}\" \"{script_path}\"")
        self.status_label.setText("Running..")

    def abort_process(self):
        """
        Attempts to terminate the running subprocess.
        """
        self.status_label.setText("Aborting..")
        self.process.terminate()
        self.process.waitForFinished(1000)
        self.status_label.setText("Aborted..")
        self.set_banner()
        self.status_label.setText("Ready..")

    def read_output(self):
        """
        Reads and formats output from the subprocess into the text edit area.
        """
        timestamp_format = QtGui.QTextCharFormat()
        timestamp_format.setForeground(QtGui.QColor("#0081FF"))
        timestamp = f'\n[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]'
        self.text_edit.setCurrentCharFormat(timestamp_format)
        self.text_edit.insertPlainText(timestamp)
        self.line_start += len(timestamp)

        prompt_format = QtGui.QTextCharFormat()
        prompt_format.setForeground(QtGui.QColor("magenta"))
        prompt = " > "
        self.text_edit.setCurrentCharFormat(prompt_format)
        self.text_edit.insertPlainText(prompt)
        self.line_start += len(prompt)

        output = str(self.process.readAll(), encoding="utf-8").rstrip()
        self.text_edit.setCurrentCharFormat(self.default_format)
        self.text_edit.insertPlainText(output)
        self.line_start += len(output)

        self.text_edit.moveCursor(QtGui.QTextCursor.End)

    def write(self, text):
        """
        Sends input to the subprocess.
        """
        self.line_start += len(text)
        self.process.write(f"{text}\n".encode())

    def eventFilter(self, obj, event):
        """
        Captures Return key presses for submitting commands to the subprocess.
        """
        if event.type() == QtCore.QEvent.KeyPress and obj is self.text_edit:
            if event.key() == QtCore.Qt.Key_Return and self.text_edit.hasFocus():
                if self.process.state():
                    command = self.text_edit.toPlainText()[self.line_start:]
                    self.write(command)
                else:
                    self.start_process()
        return super().eventFilter(obj, event)

    def set_banner(self):
        """
        Resets the terminal display to the default banner message.
        """
        banner_format = QtGui.QTextCharFormat()
        banner_format.setForeground(QtGui.QColor("grey"))
        self.text_edit.setCurrentCharFormat(banner_format)

        cwd = os.getcwd()
        self.banner_text = f"({os.path.basename(cwd)}) {cwd} > READY\n\n"
        self.text_edit.setText(self.banner_text)
        self.text_edit.moveCursor(QtGui.QTextCursor.End)
