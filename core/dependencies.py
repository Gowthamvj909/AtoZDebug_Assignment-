from fastapi import HTTPException, Request
from utils.auth_utils import verify_token
from db_operations.db import users_collection


def get_current_user(request: Request):
    """
    Retrieve the current authenticated user based on the session token.

    Args:
        request (Request): The HTTP request object containing the session cookie.

    Returns:
        dict: The user object from the database if authenticated.

    Raises:
        HTTPException: If the session token is missing, invalid, or the user is not found.
    """
    token = request.cookies.get("library_session")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = verify_token(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid session")
    user = users_collection.find_one({"username": user_id})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def check_role(user, required_role):
    """
    Verify if the user has the required role to perform an action.

    Args:
        user (dict): The user object retrieved from the database.
        required_role (str): The role required to access a resource.

    Raises:
        HTTPException: If the user does not have the required role.
    """
    if user["role"] != required_role:
        raise HTTPException(status_code=403, detail="Forbidden")