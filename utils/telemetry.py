import os
import re
import sys
import time
import json
import getpass
import logging
from paramiko import SSHClient, AutoAddPolicy


class LoggingAgent:
    """
    LoggingAgent handles telemetry data transfer to a remote server over SSH.

    This class reads telemetry configuration from a settings file using a
    PersistentDict or similar configuration management system. It parses the
    remote SSH target string, checks whether telemetry is enabled, reads local
    logs from a predefined path, and echoes them to a remote path periodically.

    Attributes:
        interval (int): Interval in seconds between telemetry uploads.
        connection (SSHClient | None): SSH connection to the remote server.
        ip (str): IP address or hostname of the remote server.
        path (str): Remote path where telemetry logs should be stored.
        username (str): SSH username for the remote connection.
        password (str): SSH password for the remote connection.
        enabled (bool): Indicates whether telemetry is currently enabled.
    """

    def __init__(self, interval=5):
        """
        Initialize the LoggingAgent and start the telemetry job scheduler.

        Args:
            interval (int, optional): Frequency in seconds to send telemetry logs.
                Defaults to 5.
        """
        self.interval = interval
        self.connection = None
        self.target = {}
        self.enabled = False

        self.load_data()
        self.schedule_job()

    def load_data(self):
        """
        Load telemetry configuration from the settings file and parse credentials.

        This method loads JSON data from the settings path defined in the `utils`
        module, and sets internal variables for SSH connection and telemetry control.
        """
        settings = json.load(open(sys.modules["utils"].PATH_SETTINGS_DATA))

        self.enabled = settings.get("telemetry_enabled", False)

        self.ip = settings.get("server")["ip"]
        self.path = os.path.join(settings.get("server")["path"], "userlogs")
        self.username = settings.get("server")["username"]
        self.password = settings.get("server")["password"]

    def set_connection(self):
        """
        Establish an SSH connection to the remote telemetry server if not already connected.

        If the connection is not established and valid credentials are available,
        a new SSH session is initiated using Paramiko. If the IP is missing,
        the method will log a debug message and exit silently.
        """
        if self.connection or not self.ip:
            if not self.ip:
                logging.debug("Cannot establish SSH connection: telemetry target not set.")
            return

        try:
            self.connection = SSHClient()
            self.connection.set_missing_host_key_policy(AutoAddPolicy())
            self.connection.connect(
                hostname=self.ip,
                username=self.username,
                password=self.password
            )
            logging.debug("SSH connection to telemetry server established.")
        except Exception as e:
            logging.debug(f"Failed to establish SSH connection: {e}")
            self.connection = None

    def echo(self, data):
        """
        Send log data to the remote telemetry server using SSH and an echo command.

        Args:
            data (str): Content of the local log to be appended to the remote file.

        If the SSH connection is not established, it attempts to create one.
        Log data is escaped for shell compatibility before sending.
        """
        if not data:
            return

        if not self.connection:
            self.set_connection()

        if not self.connection:
            logging.debug("Telemetry echo failed: no SSH connection available.")
            return

        try:
            remote_path = os.path.join(
                self.path, f"{getpass.getuser()}.log"
            ).replace("\\", "/")

            sanitized_data = re.sub(r'\\', r'\\\\\\\\', data).strip()
            cmd = f'echo "{sanitized_data}" >> {remote_path}'

            self.connection.exec_command(cmd)
            logging.debug(f"Telemetry data echoed to {remote_path}")
        except Exception as e:
            logging.debug(f"Error sending telemetry data: {e}")

    def schedule_job(self):
        """
        Run a continuous loop that sends telemetry logs at defined intervals.

        This method checks if telemetry is enabled and whether the log file exists.
        If both conditions are met, it sends the content to the remote server and
        clears the local log file. This loop runs indefinitely with a delay defined
        by `interval`.
        """
        logging.debug("Starting telemetry job loop.")

        utils = sys.modules["utils"]

        while True:
            try:
                self.load_data()

                if self.enabled and self.ip and os.path.exists(utils.PATH_LOGGER_TELEMETRY):
                    with open(utils.PATH_LOGGER_TELEMETRY, "r+") as log_file:
                        content = log_file.read()
                        if content:
                            self.echo(content)
                            log_file.seek(0)
                            log_file.truncate()
                            logging.debug("Local telemetry log sent and cleared.")
            except Exception as e:
                logging.debug(f"Telemetry job failed: {e}")

            time.sleep(self.interval)
