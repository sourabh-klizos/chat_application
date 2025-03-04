import bcrypt

class PasswordUtils:
    @staticmethod
    async def get_hashed_password(password: str) -> bytes:
        try:
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
            return hashed_password
        except Exception as e:
            # Handle any exceptions that occur during hashing
            raise Exception(f"Error occurred while hashing the password: {str(e)}")

    @staticmethod
    async def verify_password(password: str, hashed_password: bytes) -> bool:
        try:
            return bcrypt.checkpw(password.encode("utf-8"), hashed_password)
        except Exception as e:
            # Handle any exceptions that occur during verification
            raise Exception(f"Error occurred while verifying the password: {str(e)}")