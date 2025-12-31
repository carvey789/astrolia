from datetime import datetime
from typing import Optional, Dict
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from ..config import get_settings

settings = get_settings()


async def verify_google_token(token: str) -> Optional[Dict]:
    """
    Verify a Google OAuth ID token and return user info.
    Returns None if verification fails.
    """
    try:
        # Verify the token
        idinfo = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            settings.google_client_id
        )

        # Token is valid, return user info
        return {
            "google_id": idinfo["sub"],
            "email": idinfo["email"],
            "email_verified": idinfo.get("email_verified", False),
            "name": idinfo.get("name", ""),
            "picture": idinfo.get("picture"),
        }
    except ValueError:
        # Invalid token
        return None
