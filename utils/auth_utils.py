from itsdangerous import URLSafeTimedSerializer
from core.config import SECRET_KEY

serializer = URLSafeTimedSerializer(SECRET_KEY)

def create_token(user_name):
    """
    Create a secure token for a given username.

    Args:
        user_name (str): The username to encode in the token.

    Returns:
        tuple: 
            - str: The generated token.
            - int: Expiry time in seconds (default is 7 days).
    """
    token = serializer.dumps({"username": user_name})
    expiry = 60 * 60 * 24 * 7  # 7 days
    return token, expiry


def verify_token(token):
    """
    Verify a secure token and retrieve the username if valid.

    Args:
        token (str): The token to verify.

    Returns:
        str: The username if the token is valid.
        None: If the token is invalid or expired.
    """
    try:
        data = serializer.loads(token, max_age=60 * 60 * 24 * 7)
        return data["username"]
    except Exception:
        return None