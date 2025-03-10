from app.utils.logger_config import LOGGER


class ChatGroup:

    @staticmethod
    async def create_unique_group(user_a: str, user_b: str):
        """Creates a unique sorted group with a random string added."""
        try:
            if (user_a and user_b) and (user_b != "null"):
                group: str = user_a + user_b
                group = "".join(sorted(group))
                return group
            return None
        except Exception as e:
            LOGGER.error(
                "Error occurred while creating the unique group: %s",
                str(e),
                exc_info=True,
            )
            return None


# class ChatGroup:

#     @staticmethod
#     async def create_unique_group(user_a: str, user_b: str):
#         """Creates a unique sorted group using min/max."""
#         try:
#             if (user_a and user_b) and (user_b != "null"):
#                 group = min(user_a, user_b) + max(user_a, user_b)
#                 return group
#             return None
#         except Exception as e:
#             LOGGER.error(
#                 "Error occurred while creating the unique group: %s",
#                 str(e),
#                 exc_info=True,
#             )
#             return None