import keyring
import getpass
import logging
from cryptography.fernet import Fernet, InvalidToken

# Set up module-level logger
logger = logging.getLogger(__name__)

SERVICE_NAME = "Netmig"
USERNAME = getpass.getuser()

class PasswordCipher:
    def __init__(self):
        self.key = self._get_or_create_key()
        self.fernet = Fernet(self.key.encode())

    def _get_or_create_key(self) -> str:
        """
        Retrieves the encryption key from secure OS storage, or creates and stores a new one if not found.
        """
        key = keyring.get_password(SERVICE_NAME, USERNAME)
        if key:
            logger.debug("Encryption key retrieved from secure store.")
            return key

        key = Fernet.generate_key().decode()
        keyring.set_password(SERVICE_NAME, USERNAME, key)
        logger.info("New encryption key generated and saved to secure store.")
        return key

    def encrypt(self, plain_text: str) -> str:
        """
        Encrypts plain text using the Fernet key.
        Returns an empty string if input is empty.
        """
        if not plain_text:
            return ""
        encrypted = self.fernet.encrypt(plain_text.encode()).decode()
        logger.debug("Text encrypted successfully.")
        return encrypted

    def decrypt(self, cipher_text: str) -> str:
        """
        Decrypts encrypted text using the Fernet key.
        Returns an empty string if input is empty.
        Raises ValueError on decryption error.
        """
        if not cipher_text:
            return ""
        try:
            decrypted = self.fernet.decrypt(cipher_text.encode()).decode()
            logger.debug("Text decrypted successfully.")
            return decrypted
        except InvalidToken:
            logger.error("Decryption failed: Invalid token or corrupted data.")
            raise ValueError("Decryption failed: invalid key or corrupted data.")

    def reset_key(self):
        """
        Deletes the saved key from OS keyring. A new key will be generated on next use.
        WARNING: This will make previously encrypted data unreadable.
        """
        try:
            keyring.delete_password(SERVICE_NAME, USERNAME)
            logger.warning("Encryption key deleted from secure store.")
        except keyring.errors.PasswordDeleteError:
            logger.warning("No encryption key found or failed to delete.")

    def regenerate_key(self):
        """
        Deletes current key and creates a new one.
        WARNING: This makes existing encrypted data unrecoverable.
        """
        self.reset_key()
        self.key = self._get_or_create_key()
        self.fernet = Fernet(self.key.encode())
        logger.info("Encryption key regenerated.")
