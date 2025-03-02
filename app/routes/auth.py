from fastapi import APIRouter, HTTPException, status, Depends, Query, Request
from app.models.user import UserRequestModel, UserLoginModel, UserResponseModel
from pymongo.collection import Collection

# from app.utils.hashing import get_hashed_password, verify_password
from app.utils.hashing import PasswordUtils
from datetime import datetime
from app.utils.jwt_handler import create_access_token, create_refresh_token
from app.database.db import get_db
from typing import List

from app.utils.serializers import Serializers

auth_routes = APIRouter(prefix="/api/v1/auth", tags=["user"])


@auth_routes.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    request: Request, user_credential: UserRequestModel, db=Depends(get_db)
):

    try:

        user_collection: Collection = db["users"]

        user_dict = user_credential.model_dump()

        user_dict["email"] = user_dict["email"].lower()
        user_dict["username"] = user_dict["username"].lower()

        username = user_dict.get("username")
        user_email = user_dict.get("email")
        email_already_exists = await user_collection.find_one({"email": user_email})
        username_already_exists = await user_collection.find_one({"username": username})
        if email_already_exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists with this email",
            )

        if username_already_exists:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": "User already exists with this username",
                },
            )

        user_dict["created_at"] = datetime.now()
        # user_dict["password"] = await get_hashed_password(user_dict["password"])
        user_dict["password"] = await PasswordUtils.get_hashed_password(
            user_dict["password"]
        )

        await user_collection.insert_one(user_dict)
        return {"message": "User account created successfully."}
    except HTTPException as http_error:
        raise HTTPException(
            status_code=http_error.status_code,
            detail=http_error.detail,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )


@auth_routes.post(
    "/login",
    status_code=status.HTTP_200_OK,
)
async def user_login(user_credential: UserLoginModel, db=Depends(get_db)):

    try:
        print(user_credential)
        user_collection: Collection = db["users"]

        user_dict = user_credential.model_dump()
        email = user_dict["email"].lower()
        password = user_dict.get("password")

        user_instance = await user_collection.find_one({"email": email})
        if not user_instance:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        hashed_password = user_instance.get("password")
        check_password = await PasswordUtils.verify_password(password, hashed_password)

        if not check_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        user_id = str(user_instance.get("_id"))

        access_token = await create_access_token(user_id)
        refresh_token = await create_refresh_token(user_id=user_id, db=db)

        response = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_id": user_id,
        }

        return response

    except HTTPException as http_error:
        raise HTTPException(
            status_code=http_error.status_code,
            detail=http_error.detail,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )


@auth_routes.get(
    "/users",
    response_model=List[UserResponseModel],
    status_code=status.HTTP_200_OK,
)
async def retrive_active_users(db=Depends(get_db)):

    try:
        user_collection: Collection = db["users"]
        users_cursor = user_collection.find({}, {"password": 0})
        users_list = await users_cursor.to_list()
        users = await Serializers.convert_ids_to_strings(users_list)

        return users

    except HTTPException as http_error:
        raise HTTPException(
            status_code=http_error.status_code,
            detail=http_error.detail,
        )

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )
