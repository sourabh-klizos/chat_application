from fastapi import status, HTTPException, Security

from fastapi.security import OAuth2PasswordBearer

from app.utils.jwt_handler import decode_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_current_user_id(token: str = Security(oauth2_scheme)):
    """
    Returns the user ID from a valid JWT access token.

    :param token: OAuth2 access token.
    :raises HTTPException: If token is missing, invalid, or an error occurs.
    """
    try:
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )

        user_details = await decode_jwt(token, "access_token")

        if not user_details:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not a valid token ",
            )

        if "user_id" not in user_details:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not a valid token",
            )

        return user_details["user_id"]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )
