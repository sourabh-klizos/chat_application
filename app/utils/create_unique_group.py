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
            # Handle any exceptions that may occur during group creation
            print(f"Error occurred while creating the unique group: {e}")
            return None
