"""
Stream Objects

This module defines custom stream objects (`StdoutStream`, `StderrStream`) for redirecting
standard output and error streams to Qt signals. These streams can be connected to widgets
(e.g., QTextEdit) in a PyQt5 GUI to display real-time output and errors.
"""

import sys
from PyQt5 import QtCore


class StdoutStream(QtCore.QObject):
    """
    A custom stream that redirects standard output (stdout) to a Qt signal.

    This allows GUI components to receive and display printed output dynamically.
    It is especially useful for logging or console-like widgets in a PyQt5 application.
    """

    text_written = QtCore.pyqtSignal(str)
    """Signal emitted when text is written to stdout."""

    def flush(self):
        """
        No-op flush method for compatibility with file-like interfaces.
        """
        pass

    def fileno(self):
        """
        Return a dummy file descriptor.

        Returns:
            int: A dummy value (-1) to mimic file-like behavior.
        """
        return -1

    def write(self, msg):
        """
        Write text to the stream by emitting it through a Qt signal.

        Args:
            msg (str): The message to emit.
        """
        if not self.signalsBlocked():
            self.text_written.emit(msg)


class StderrStream(QtCore.QObject):
    """
    A custom stream that redirects standard error (stderr) to a Qt signal.

    This allows GUI components to receive and display error output in real-time,
    aiding in error reporting and debugging within GUI applications.
    """

    text_written = QtCore.pyqtSignal(str)
    """Signal emitted when text is written to stderr."""

    def flush(self):
        """
        No-op flush method for compatibility with file-like interfaces.
        """
        pass

    def fileno(self):
        """
        Return a dummy file descriptor.

        Returns:
            int: A dummy value (-1) to mimic file-like behavior.
        """
        return -1

    def write(self, msg):
        """
        Write error text to the stream by emitting it through a Qt signal.

        Args:
            msg (str): The error message to emit.
        """
        if not self.signalsBlocked():
            self.text_written.emit(msg)

    def excepthook(self, type, exception, traceback):
        """
        Custom exception hook that delegates to the system default handler.

        Args:
            type (Type[BaseException]): The exception class.
            exception (BaseException): The exception instance.
            traceback (traceback): The traceback object.
        """
        sys.__excepthook__(type, exception, traceback)
