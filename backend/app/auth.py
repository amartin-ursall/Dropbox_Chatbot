"""
Dropbox OAuth2 authentication module - AD-5
Handles OAuth2 flow and session management with persistence
"""
from typing import Optional, Dict
import httpx
from fastapi import HTTPException
from urllib.parse import urlencode
import json
import os
from pathlib import Path

# Dropbox OAuth2 configuration
DROPBOX_APP_KEY = "rvsal3as0j73d3y"
DROPBOX_APP_SECRET = "h933ko0ruapay5i"
DROPBOX_REDIRECT_URI = "http://localhost:8000/auth/dropbox/callback"

# Session storage file path
SESSION_FILE = Path(os.path.expanduser("~")) / ".dropbox_chatbot_session.json"

# For simplicity, using a single session key (in production, use session IDs per user)
SESSION_KEY = "default_session"


def load_sessions() -> Dict[str, Dict]:
    """Load sessions from file"""
    if SESSION_FILE.exists():
        try:
            with open(SESSION_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading sessions: {e}")
            return {}
    return {}


def save_sessions(sessions: Dict[str, Dict]) -> None:
    """Save sessions to file"""
    try:
        with open(SESSION_FILE, 'w') as f:
            json.dump(sessions, f, indent=2)
    except Exception as e:
        print(f"Error saving sessions: {e}")


# Load sessions from file on startup
sessions: Dict[str, Dict] = load_sessions()


def generate_auth_url() -> str:
    """
    Generate Dropbox OAuth2 authorization URL

    Returns:
        str: Full OAuth2 authorization URL
    """
    params = {
        "client_id": DROPBOX_APP_KEY,
        "redirect_uri": DROPBOX_REDIRECT_URI,
        "response_type": "code",
        "token_access_type": "offline"  # For refresh token
    }
    return f"https://www.dropbox.com/oauth2/authorize?{urlencode(params)}"


async def exchange_code_for_token(code: str) -> Dict:
    """
    Exchange authorization code for access token

    Args:
        code: Authorization code from Dropbox callback

    Returns:
        dict: Token response from Dropbox

    Raises:
        HTTPException: If token exchange fails
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.dropboxapi.com/oauth2/token",
            data={
                "code": code,
                "grant_type": "authorization_code",
                "client_id": DROPBOX_APP_KEY,
                "client_secret": DROPBOX_APP_SECRET,
                "redirect_uri": DROPBOX_REDIRECT_URI,
            }
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail="Failed to exchange authorization code for token"
            )

        return response.json()


def store_session(token_data: Dict) -> None:
    """
    Store session data persistently

    Args:
        token_data: Token data from Dropbox
    """
    sessions[SESSION_KEY] = {
        "access_token": token_data.get("access_token"),
        "account_id": token_data.get("account_id"),
        "uid": token_data.get("uid"),
        "token_type": token_data.get("token_type"),
    }
    save_sessions(sessions)


def get_session() -> Optional[Dict]:
    """
    Get current session data

    Returns:
        dict or None: Session data if exists
    """
    return sessions.get(SESSION_KEY)


def clear_session() -> None:
    """Clear current session"""
    if SESSION_KEY in sessions:
        del sessions[SESSION_KEY]
        save_sessions(sessions)


def is_authenticated() -> bool:
    """
    Check if user is authenticated

    Returns:
        bool: True if authenticated
    """
    session = get_session()
    return session is not None and "access_token" in session


def get_access_token() -> Optional[str]:
    """
    Get Dropbox access token from session

    Returns:
        str or None: Access token if authenticated

    Raises:
        HTTPException: If not authenticated
    """
    session = get_session()
    if not session or "access_token" not in session:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. Please login with Dropbox first."
        )
    return session["access_token"]