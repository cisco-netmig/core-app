"""
Threads

This module contains threaded classes used for:
1. Checking for the latest version of the application from a remote GitHub JSON file.
2. Downloading and extracting repositories from a GitHub ZIP archive.
3. Fetching and installing Python packages from a remote requirements.txt file.
4. Emitting timed messages used for countdowns, typically during application restarts.

These classes are designed to run in the background using QThread, ensuring the UI remains responsive.
"""

import os
import sys
import logging
import shutil
import subprocess
import re
import requests
import getpass
import base64
import git
from zipfile import ZipFile

from PyQt5 import QtCore
from requests import get, ConnectionError, RequestException
from paramiko import SSHClient, AutoAddPolicy


class CheckGitVersion(QtCore.QThread):
    """
    QThread for asynchronously checking the latest version of the application
    from a remote JSON hosted on GitHub.

    Signals:
        version_signal (str): Emitted when a valid version is fetched.
        message_signal (str): Emitted with any error or informational messages.
    """
    version_signal = QtCore.pyqtSignal(str)
    message_signal = QtCore.pyqtSignal(str)

    def __init__(self, app_url):
        """
        Initialize the thread with a GitHub URL.

        Args:
            app_url (str): URL of the remote JSON containing version info.
        """
        super().__init__()
        self.app_url = app_url
        logging.debug(f"[CheckGitVersion] Initialized with URL: {self.app_url}")

    def run(self):
        """Fetch the latest version info from the GitHub repository."""
        logging.debug(f"[CheckGitVersion] Starting version check thread.")
        try:
            logging.debug(f"[CheckGitVersion] Sending request to: {self.app_url}")
            response = get(self.app_url)
            logging.debug(f"[CheckGitVersion] Response status code: {response.status_code}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    version = data.get('version', '')
                    logging.debug(f"[CheckGitVersion] Parsed version: {version}")

                    if version:
                        self.version_signal.emit(version)
                        logging.debug(f"[CheckGitVersion] Emitted version signal.")
                    else:
                        msg = "Version key not found in JSON response."
                        self.message_signal.emit(msg)
                        logging.debug(f"[CheckGitVersion] {msg}")
                except ValueError:
                    msg = "Failed to parse JSON from response."
                    self.message_signal.emit(msg)
                    logging.debug(f"[CheckGitVersion] {msg}")
            else:
                msg = f"Failed to get version: {self.app_url} (Status code: {response.status_code})"
                self.message_signal.emit(msg)
                logging.debug(f"[CheckGitVersion] {msg}")
        except ConnectionError:
            msg = "Cannot connect to Git!"
            self.message_signal.emit(msg)
            logging.debug(f"[CheckGitVersion] {msg}")
        except RequestException as e:
            msg = f"Request failed: {str(e)}"
            self.message_signal.emit(msg)
            logging.debug(f"[CheckGitVersion] {msg}")


class DownloadRepo(QtCore.QThread):
    """
    QThread for downloading a zipped GitHub repository and extracting it
    to a specified working directory.

    Signals:
        success_signal (int): Emits the HTTP response code after completion.
    """
    success_signal = QtCore.pyqtSignal(int)

    def __init__(self, repo_url: str, cache_dir: str, working_dir: str):
        """
        Initialize the thread with URLs and paths.

        Args:
            repo_url (str): URL to download the repository ZIP.
            cache_dir (str): Path to cache the downloaded ZIP.
            working_dir (str): Path where the repo will be extracted.
        """
        super().__init__()
        self.repo_url = repo_url
        self.cache_dir = cache_dir
        self.working_dir = working_dir
        self.repo_file_path = os.path.join(self.cache_dir, 'netmig')
        logging.debug(
            f"[DownloadRepo] Initialized with repo_url={repo_url}, cache_dir={cache_dir}, working_dir={working_dir}")

    def run(self):
        """Download and extract the GitHub repo into the working directory."""
        logging.debug("[DownloadRepo] Starting download and extraction process.")
        try:
            logging.debug(f"[DownloadRepo] Sending GET request to {self.repo_url}")
            response = get(self.repo_url)
            logging.debug(f"[DownloadRepo] Received response with status code: {response.status_code}")

            if response.status_code != 200:
                logging.debug("[DownloadRepo] Non-200 response, aborting.")
                self.success_signal.emit(response.status_code)
                return

            os.makedirs(self.cache_dir, exist_ok=True)
            logging.debug(f"[DownloadRepo] Ensured cache directory exists: {self.cache_dir}")

            if os.path.exists(self.repo_file_path):
                os.remove(self.repo_file_path)
                logging.debug(f"[DownloadRepo] Removed existing cache file: {self.repo_file_path}")

            with open(self.repo_file_path, 'wb') as f:
                f.write(response.content)
                logging.debug(f"[DownloadRepo] Wrote repo ZIP to: {self.repo_file_path}")

            with ZipFile(self.repo_file_path, 'r') as zip_file:
                logging.debug("[DownloadRepo] Opened ZIP file for extraction.")
                for member in zip_file.namelist()[1:]:  # Skip root folder
                    member_path = member.split('/')
                    relative_path = os.path.join(*member_path[1:])
                    target_path = os.path.join(self.working_dir, relative_path)
                    target_dir = os.path.dirname(target_path)

                    os.makedirs(target_dir, exist_ok=True)

                    if not member.endswith('/'):
                        with zip_file.open(member) as source, open(target_path, 'wb') as target:
                            shutil.copyfileobj(source, target)
                            logging.debug(f"[DownloadRepo] Extracted {relative_path} to {target_path}")

            logging.debug("[DownloadRepo] Extraction complete. Emitting success signal.")
            self.success_signal.emit(response.status_code)

        except RequestException as e:
            logging.debug(f"[DownloadRepo] RequestException occurred: {e}")
            self.success_signal.emit(0)
        except Exception as e:
            logging.debug(f"[DownloadRepo] Unexpected exception occurred: {e}", exc_info=True)
            self.success_signal.emit(0)


class GetRequirements(QtCore.QThread):
    """
    QThread for fetching and installing Python dependencies from a remote
    requirements.txt file.

    Signals:
        message_signal (str): Emits log and error messages.
    """
    message_signal = QtCore.pyqtSignal(str)

    def __init__(self, requirements_url: str):
        """
        Initialize with the URL pointing to the requirements.txt.

        Args:
            requirements_url (str): Remote URL for the requirements file.
        """
        super().__init__()
        self.requirements_url = requirements_url
        self.requirements = []
        logging.debug(f"[GetRequirements] Initialized with URL: {requirements_url}")

    def run(self):
        """Fetch the requirements.txt file and install packages using pip."""
        logging.debug("[GetRequirements] Starting run method.")
        try:
            self.message_signal.emit('Gathering requirements..')
            logging.debug(f"[GetRequirements] Sending GET request to: {self.requirements_url}")
            response = get(self.requirements_url)

            if response.status_code == 200:
                self.requirements = response.text.splitlines()
                logging.debug(f"[GetRequirements] Retrieved {len(self.requirements)} packages.")
                self.exec_pip()
            else:
                error_msg = f'Failed to fetch requirements (Status: {response.status_code})'
                logging.debug(f"[GetRequirements] {error_msg}")
                self.message_signal.emit(error_msg)

        except RequestException as e:
            error_msg = f'Connection error while fetching requirements: {e}'
            logging.debug(f"[GetRequirements] {error_msg}")
            self.message_signal.emit(error_msg)

    def exec_pip(self):
        """Loop through the list of requirements and install them via pip."""
        logging.debug("[GetRequirements] Starting package installation loop.")
        for package in self.requirements:
            package = package.strip()
            if not package:
                continue

            logging.debug(f"[GetRequirements] Installing: {package}")
            self.message_signal.emit(f'Installing Python package: {package}...')

            try:
                process = subprocess.run(
                    [sys.executable, "-m", "pip", "install", package],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
                if process.returncode == 0:
                    logging.debug(f"[GetRequirements] Successfully installed: {package}")
                    self.message_signal.emit(f'Successfully installed: {package}')
                else:
                    logging.debug(f"[GetRequirements] Installation failed for: {package}")
                    self.message_signal.emit(f'Failed to install: {package}')
            except Exception as e:
                error_msg = f'Error installing {package}: {e}'
                logging.debug(f"[GetRequirements] {error_msg}")
                self.message_signal.emit(error_msg)


class WaitRestart(QtCore.QThread):
    """
    QThread for emitting countdown messages before restarting the application.

    Signals:
        message_signal (str): Emits countdown text like "Restarting in X seconds..."
    """
    message_signal = QtCore.pyqtSignal(str)

    def __init__(self, countdown_start=5, parent=None):
        """
        Initialize the countdown thread.

        Args:
            countdown_start (int): Number of seconds before restart begins.
            parent (QObject): Optional parent object.
        """
        super().__init__(parent)
        self.countdown_start = countdown_start
        self._is_running = True
        logging.debug(f"[WaitRestart] Initialized with countdown_start = {countdown_start}")

    def run(self):
        """Emit countdown messages every second."""
        logging.debug("[WaitRestart] Countdown started.")
        for sec in range(self.countdown_start, 0, -1):
            if not self._is_running:
                logging.debug("[WaitRestart] Countdown stopped early.")
                break
            QtCore.QThread.sleep(1)
            logging.debug(f"[WaitRestart] Emitting countdown: Restarting in {sec} seconds...")
            self.message_signal.emit(f'Restarting in {sec} seconds...')
        logging.debug("[WaitRestart] Countdown finished.")

    def stop(self):
        """Stop the countdown."""
        logging.debug("[WaitRestart] Stop signal received.")
        self._is_running = False


class CheckAuthentication(QtCore.QThread):
    """
    CheckAuthentication is a QThread that attempts to authenticate to a remote device
    using Netmiko and updates a QLabel with the authentication status.

    This class is useful for non-blocking UI operations when testing SSH credentials.

    Attributes:
        ip (str): IP address of the remote device.
        username (str): SSH username.
        password (str): SSH password.
        msg_label (QLabel): QLabel to display authentication status.
    """

    def __init__(self, ip, username, password, msg_label):
        """
        Initialize the thread with target device credentials and UI label.

        Args:
            ip (str): IP address of the remote device.
            username (str): Username for SSH login.
            password (str): Password for SSH login.
            msg_label (QLabel): QLabel instance to display authentication messages.
        """
        super().__init__()
        self.ip = ip
        self.username = username
        self.password = password
        self.msg_label = msg_label

    def run(self):
        """
        Executes the authentication check in a separate thread.

        Uses Netmiko to attempt an SSH connection and updates the QLabel
        with success or failure status.
        """
        self.msg_label.setText("Authenticating...")

        try:
            from netmiko import ConnectHandler

            logging.debug(f"Attempting authentication to {self.ip}")
            ConnectHandler(
                ip=self.ip,
                username=self.username,
                password=self.password,
                device_type="linux"
            )
            self.msg_label.setText("Success !!")
            self.msg_label.setStyleSheet("color:green")
            logging.info("Authentication successful.")
        except Exception as err:
            self.msg_label.setText("Failed !!")
            self.msg_label.setStyleSheet("color:red")
            logging.error(f"Authentication failed: {err}")


class GitSync(QtCore.QThread):
    """
    A QThread-based class that asynchronously synchronizes remote script metadata and assets
    from a list of Git repositories containing submodules (scripts).

    Emits:
        script_data_chunk (dict): Emitted for each script UUID after its data is fetched and processed.
    """

    script_data_chunk = QtCore.pyqtSignal(dict)

    def __init__(self, base_urls, local_cache):
        """
        Initializes the GitSync thread.

        Args:
            base_urls (list[str]): List of parent repository URLs containing submodules.
            local_cache (dict): Dictionary of locally cached script metadata, keyed by UUID.
        """
        super().__init__()
        self.base_urls = [url.rstrip('/') for url in base_urls]
        self.local_cache = local_cache

    def run(self):
        """
        Thread entry point.

        Handles both parent repositories with submodules and direct script repositories.
        """
        for base_url in self.base_urls:
            try:
                # Try parsing as a parent repo with submodules
                submodules = self.get_submodules(base_url)

                if submodules:
                    for module_name, module_url in submodules.items():
                        script_data = self.process_script(module_url)
                        if script_data:
                            self.script_data_chunk.emit(script_data)
                else:
                    # If no submodules, treat the base_url as a direct script repo
                    script_data = self.process_script(base_url)
                    if script_data:
                        self.script_data_chunk.emit(script_data)

            except Exception as e:
                logging.error(f"[Repo Sync Fail] {base_url}: {e}")

    def process_script(self, module_url):
        """
        Fetches and processes a script's metadata, README, and icon from its remote module URL.

        Args:
            module_url (str): The URL of the submodule repository.

        Returns:
            dict or None: A dictionary keyed by script UUID containing script metadata,
                          or None if the fetch fails or UUID is missing.
        """
        meta_url = f"{module_url}/raw/master/__meta__"
        try:
            resp = requests.get(meta_url, timeout=5)
            resp.raise_for_status()
            meta_data = resp.json()

            script_uuid = meta_data.get("uuid")
            if not script_uuid:
                return None

            script_data = {
                "uuid": script_uuid,
                "source": "git",
                "module": module_url,
                "load": True,
                **meta_data,
                "readme": self.fetch_readme(module_url),
                "icon_data": self.fetch_icon(module_url),
            }

            local_meta = self.local_cache.get(script_uuid, {})
            script_data["status"] = self.determine_status(meta_data, local_meta)

            return {script_uuid: script_data}

        except Exception as e:
            logging.error(f"[Meta Fetch Fail] {meta_url}: {e}")
            return None

    def get_submodules(self, base_url):
        """
        Fetches and parses the `.gitmodules` file from the parent repository to extract submodule info.

        Args:
            base_url (str): The URL of the parent repository.

        Returns:
            dict: A dictionary mapping submodule names to their Git URLs.
        """
        gitmodules_url = f"{base_url}/raw/master/.gitmodules"
        try:
            resp = requests.get(gitmodules_url, timeout=5)
            resp.raise_for_status()

            content = resp.text
            submodules = {}

            pattern = re.compile(
                r'\[submodule "(?P<name>[^"]+)"\]\s+path\s*=\s*(?P<path>[^\n]+)\s+url\s*=\s*(?P<url>[^\n]+)',
                re.MULTILINE
            )

            for match in pattern.finditer(content):
                name = match.group("name").strip()
                url = match.group("url").strip()
                submodules[name] = url

            return submodules

        except Exception as e:
            logging.debug(f"[Fetch Fail: .gitmodules] {gitmodules_url}: {e}")
            return {}

    def fetch_readme(self, module_url):
        """
        Fetches the README markdown content from a script submodule.

        Args:
            module_url (str): The URL of the submodule repository.

        Returns:
            str: README content if found, else an empty string.
        """
        readme_url = f"{module_url}/raw/master/README.md"
        try:
            resp = requests.get(readme_url, timeout=5)
            if resp.ok:
                return resp.text
        except Exception:
            pass
        return ""

    def fetch_icon(self, module_url):
        """
        Fetches and encodes the icon image for a script submodule.

        Args:
            module_url (str): The URL of the submodule repository.

        Returns:
            str: Base64-encoded icon data, or an empty string if fetch fails.
        """
        icon_url = f"{module_url}/raw/master/__icon__.ico"
        try:
            resp = requests.get(icon_url, timeout=5)
            if resp.ok:
                return base64.b64encode(resp.content).decode("utf-8")
        except Exception:
            pass
        return ""

    def determine_status(self, meta_data, local_meta):
        """
        Compares local and remote metadata to determine the sync status.

        Args:
            meta_data (dict): Remote metadata for the script.
            local_meta (dict): Cached local metadata for the script.

        Returns:
            str: One of 'install', 'update', or 'installed'.
        """
        if not local_meta:
            return "install"
        elif meta_data.get("version") != local_meta.get("version"):
            return "update"
        return "installed"


class GitInstaller(QtCore.QThread):
    """
    A QThread class that performs cloning or updating of a Git repository in the background
    to prevent blocking the main UI thread.

    Emits:
        finished (bool, str, str): Emitted when the operation completes.
            - bool: True if successful, False otherwise.
            - str: Script name.
            - str: Error message if any, else an empty string.
    """

    finished = QtCore.pyqtSignal(bool, str, str)

    def __init__(self, script_data):
        """
        Initializes the GitInstaller thread.

        Args:
            script_data (dict): Metadata of the script including 'module' (repo URL) and 'name'.
        """
        super().__init__()
        self.script_data = script_data

    def run(self):
        """
        Executes the clone or pull operation for the specified Git repository.
        If the repository already exists, it pulls the latest changes;
        otherwise, it clones the repository into the designated scripts directory.
        Emits the result using the `finished` signal.
        """
        repo_url = self.script_data.get("module")
        script_name = self.script_data.get("name")
        repo_name = repo_url.rstrip("/").split("/")[-1]
        script_path = os.path.join(sys.modules["utils"].PATH_SCRIPTS_DIR, repo_name)

        try:
            if os.path.exists(script_path):
                logging.debug(f"Updating existing repository for {script_name}")
                repo = git.Repo(script_path)
                repo.remotes.origin.pull()
                logging.info(f"Successfully updated script {script_name}")
            else:
                logging.debug(f"Cloning repository for {script_name} from {repo_url}")
                git.Repo.clone_from(repo_url, script_path)
                logging.info(f"Successfully installed script {script_name}")

            self.finished.emit(True, script_name, "")
        except Exception as e:
            logging.error(f"Failed to install/update script {script_name}: {e}")
            self.finished.emit(False, script_name, str(e))