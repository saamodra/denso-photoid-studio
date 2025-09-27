"""
Authentication module for ID Card Photo Machine
Handles password hashing, verification, and user authentication
"""
import hashlib
import secrets
import logging
from typing import Optional, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

logger = logging.getLogger(__name__)

class AuthManager:
    """Manages user authentication and password security"""

    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize AuthManager with optional secret key
        If no secret key provided, generates a new one
        """
        if secret_key:
            self.secret_key = secret_key.encode()
        else:
            # Generate a new secret key (in production, this should be stored securely)
            self.secret_key = Fernet.generate_key()

        # Create Fernet cipher for encryption/decryption
        self.cipher = Fernet(self.secret_key)

    def hash_password(self, password: str) -> str:
        """
        Hash a password using PBKDF2 with SHA-256

        Args:
            password: Plain text password

        Returns:
            Hashed password string
        """
        try:
            # Generate a random salt
            salt = secrets.token_bytes(32)

            # Create PBKDF2 key derivation function
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,  # High iteration count for security
            )

            # Derive key from password
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))

            # Combine salt and key for storage
            hashed = base64.urlsafe_b64encode(salt + key).decode()

            logger.info("Password hashed successfully")
            return hashed

        except Exception as e:
            logger.error(f"Failed to hash password: {e}")
            raise

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash

        Args:
            password: Plain text password to verify
            hashed_password: Stored hashed password

        Returns:
            True if password matches, False otherwise
        """
        try:
            # Decode the stored hash
            stored_data = base64.urlsafe_b64decode(hashed_password.encode())

            # Extract salt and key
            salt = stored_data[:32]
            stored_key = stored_data[32:]

            # Create PBKDF2 key derivation function with same parameters
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )

            # Derive key from provided password
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))

            # Compare keys
            is_valid = secrets.compare_digest(key, stored_key)

            if is_valid:
                logger.info("Password verification successful")
            else:
                logger.warning("Password verification failed")

            return is_valid

        except Exception as e:
            logger.error(f"Failed to verify password: {e}")
            return False

    def encrypt_data(self, data: str) -> str:
        """
        Encrypt sensitive data using Fernet encryption

        Args:
            data: Plain text data to encrypt

        Returns:
            Encrypted data string
        """
        try:
            encrypted_data = self.cipher.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Failed to encrypt data: {e}")
            raise

    def decrypt_data(self, encrypted_data: str) -> str:
        """
        Decrypt data using Fernet decryption

        Args:
            encrypted_data: Encrypted data string

        Returns:
            Decrypted plain text data
        """
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.cipher.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt data: {e}")
            raise

    def generate_secure_token(self, length: int = 32) -> str:
        """
        Generate a secure random token

        Args:
            length: Length of token in bytes

        Returns:
            Base64 encoded secure token
        """
        return base64.urlsafe_b64encode(secrets.token_bytes(length)).decode()

# Global authentication manager instance
auth_manager = AuthManager()
