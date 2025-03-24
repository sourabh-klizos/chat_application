from app.utils.logger_config import LOGGER


class ChatGroup:

    @staticmethod
    async def create_unique_group(user_a: str, user_b: str):
        """Creates a unique group ID without hashing."""
        try:

            if user_a and user_b and user_b != "null":
                return f"{min(user_a, user_b)}-{max(user_a, user_b)}"
        except Exception as e:
            LOGGER.error(
                "Error occurred while creating the unique group: %s",
                str(e),
                exc_info=True,
            )
        return None

