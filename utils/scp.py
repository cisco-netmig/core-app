"""
scp.py

Provides an SCP wrapper for simplified file transfers over SSH using Paramiko and SCPClient.
Supports both upload and download operations with automatic handling of folders.
"""

import os
from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient


class SCP(SSHClient):
    """
    SCP wrapper class for file transfers over SSH.

    Inherits from paramiko.SSHClient to enable SCP-based file upload/download
    using an SSH connection.
    """

    def __init__(self, hostname: str, username: str, password: str):
        """
        Initialize the SSH connection with the remote host.

        Args:
            hostname (str): Remote host IP or hostname.
            username (str): SSH username.
            password (str): SSH password.
        """
        super().__init__()
        self.set_missing_host_key_policy(AutoAddPolicy())
        logging.info(f"Connecting to {hostname} as {username}")
        self.connect(hostname=hostname, username=username, password=password)
        logging.info("SSH connection established.")

    def _with_scp_client(self, action: str, *args, **kwargs):
        """
        Perform an SCP action (e.g., 'put' or 'get') using a temporary SCPClient.

        Args:
            action (str): The SCPClient method to invoke ('put' or 'get').
            *args: Positional arguments for the SCPClient method.
            **kwargs: Keyword arguments for the SCPClient method.

        Returns:
            Any: Result of the invoked SCPClient method.
        """
        logging.debug(f"Executing SCP action '{action}' with args={args} kwargs={kwargs}")
        with SCPClient(self.get_transport()) as scp:
            result = getattr(scp, action)(*args, **kwargs)
        logging.debug(f"Action '{action}' completed.")
        return result

    def put(self, local: str, remote: str):
        """
        Upload a file or directory to the remote server.

        Args:
            local (str): Path to the local file or directory.
            remote (str): Destination path on the remote server.
        """
        logging.info(f"Uploading '{local}' to '{remote}'")
        self._with_scp_client('put', local, remote, recursive=os.path.isdir(local))
        logging.debug(f"Upload of '{local}' finished.")

    def get(self, remote: str, local: str):
        """
        Download a file or directory from the remote server.

        Args:
            remote (str): Path to the remote file or directory.
            local (str): Destination path on the local machine.

        Raises:
            Exception: Propagates SCP errors unless it's a non-regular file (e.g., directory),
                       in which case it retries recursively.
        """
        logging.info(f"Downloading '{remote}' to '{local}'")
        try:
            self._with_scp_client('get', remote, local)
        except Exception as error:
            logging.warning(f"Error during download: {error}")
            if 'not a regular file' in str(error):
                logging.debug("Retrying download with recursive=True")
                self._with_scp_client('get', remote, local, recursive=True)
            else:
                raise
        logging.debug(f"Download of '{remote}' finished.")

    def transfer(self, local: str, remote: str, direction: str):
        """
        Transfer a file or directory based on direction ('get' or 'put').

        Args:
            local (str): Local path for upload or download.
            remote (str): Remote path for upload or download.
            direction (str): Either 'get' (download) or 'put' (upload).
        """
        logging.info(f"Starting transfer: direction='{direction}'")
        if direction == 'get':
            self.get(remote, local)
        else:
            self.put(local, remote)
        logging.info("Transfer completed.")