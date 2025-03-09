import bcrypt
from app.utils.logger_config import LOGGER

class PasswordUtils:
    """
    Utility class for password hashing and verification.
    """

    @staticmethod
    async def get_hashed_password(password: str) -> bytes:
        """Returns a hashed version of the given password."""
        try:
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
            return hashed_password
        except Exception as e:
            LOGGER.error("Error occurred while hashing the password: %s", str(e), exc_info=True)
            raise Exception(f"Error occurred while hashing the password: {str(e)}")

    @staticmethod
    async def verify_password(password: str, hashed_password: bytes) -> bool:
        """Verifies if the provided password matches the hashed password."""
        try:
            return bcrypt.checkpw(password.encode("utf-8"), hashed_password)
        except Exception as e:
            LOGGER.error("Error occurred while verifying the password: %s", str(e), exc_info=True)
            raise Exception(f"Error occurred while verifying the password: {str(e)}")
