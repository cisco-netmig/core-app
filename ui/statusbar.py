"""
Status Bar

This module defines the StatusBar class, which provides a customized QStatusBar
for the Netmig main window. It includes UI indicators and toggle buttons for
stream mode, telemetry, logging level, repository status, and version info.
"""

from PyQt5 import QtWidgets, QtCore


class StatusBar(QtWidgets.QStatusBar):
    """
    Custom status bar for Netmig with interactive widgets for various system states.

    Attributes:
        mainwindow (QMainWindow): Reference to the main application window.
        stream_button (QPushButton): Button to toggle stream mode.
        telemetry_button (QPushButton): Button to toggle telemetry logging.
        logging_button (QPushButton): Displays current logging level.
        repo_button (QPushButton): Indicates repository connectivity status.
        version_button (QPushButton): Displays the Netmig version.
    """

    def __init__(self, mainwindow):
        """
        Initialize the status bar and add system indicator widgets.

        Args:
            mainwindow (QMainWindow): The main application window.
        """
        super().__init__(mainwindow)
        self.mainwindow = mainwindow

        # Sync code soures button
        self.sync_button = QtWidgets.QPushButton("Sync", parent=self)
        self.sync_button.setIcon(self.mainwindow.icons['sync-grey'])
        self.sync_button.setIconSize(QtCore.QSize(16, 16))
        self.sync_button.setToolTip('Sync Code Sources')
        self.sync_button.setFixedWidth(70)
        self.sync_button.setFixedHeight(25)
        self.sync_button.clicked.connect(self.mainwindow.sync_code_sources)
        self.addPermanentWidget(self.sync_button)

        # Stream toggle button
        self.stream_button = QtWidgets.QPushButton(self)
        self.stream_button.setIcon(self.mainwindow.icons['stream-grey'])
        self.stream_button.setIconSize(QtCore.QSize(16, 16))
        self.stream_button.setFixedWidth(100)
        self.stream_button.setFixedHeight(25)
        self.stream_button.setToolTip('Toggle Stream')
        self.stream_button.clicked.connect(self.toggle_stream)
        self.addPermanentWidget(self.stream_button)

        # Telemetry toggle button
        self.telemetry_button = QtWidgets.QPushButton(self)
        self.telemetry_button.setIcon(self.mainwindow.icons['telemetry-grey'])
        self.telemetry_button.setIconSize(QtCore.QSize(16, 16))
        self.telemetry_button.setToolTip('Toggle Telemetry')
        self.telemetry_button.setFixedWidth(80)
        self.telemetry_button.setFixedHeight(25)
        self.telemetry_button.clicked.connect(self.toggle_telemetry)
        self.addPermanentWidget(self.telemetry_button)

        # Log level display
        self.logging_button = QtWidgets.QPushButton(self)
        self.logging_button.setIcon(self.mainwindow.icons['logging-grey'])
        self.logging_button.setIconSize(QtCore.QSize(16, 16))
        self.logging_button.setToolTip('Logging')
        self.logging_button.setFixedWidth(70)
        self.logging_button.setFixedHeight(25)
        self.addPermanentWidget(self.logging_button)

        # Version display
        self.version_button = QtWidgets.QPushButton(self)
        self.version_button.setIcon(self.mainwindow.icons['version-grey'])
        self.version_button.setIconSize(QtCore.QSize(16, 16))
        self.version_button.setFixedWidth(120)
        self.version_button.setFixedHeight(25)
        self.addPermanentWidget(self.version_button)


    def toggle_stream(self):
        """
        Toggle between QStream and Console output modes.

        """
        stream = self.mainwindow.settings.get("logging_stream")
        stream = 'Console' if stream == 'QStream' else 'QStream'
        self.mainwindow.settings['logging_stream'] = stream
        self.mainwindow.logger_dock.set_stream()
        self.stream_button.setText(stream)

    def toggle_telemetry(self):
        """
        Toggle telemetry logging.

        """
        telemetry_enabled = self.mainwindow.settings.get('telemetry_enabled', False)
        self.mainwindow.settings['telemetry_enabled'] = not telemetry_enabled
        self.mainwindow.logger_dock.set_telemetry_logger()
        self.telemetry_button.setText("Active" if not telemetry_enabled else "Inactive")
