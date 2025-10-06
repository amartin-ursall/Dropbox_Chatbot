"""
Dropbox helper functions
Helper utilities for interacting with Dropbox API
"""
import httpx
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


async def list_folders_in_path(access_token: str, path: str = "") -> List[str]:
    """
    List all folders in a specific Dropbox path

    Args:
        access_token: Dropbox access token
        path: Path to list (empty string for root)

    Returns:
        List of folder names (not full paths, just names)
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "path": path if path else "",
        "recursive": False,
        "include_deleted": False,
        "include_has_explicit_shared_members": False,
        "include_mounted_folders": True
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.dropboxapi.com/2/files/list_folder",
                headers=headers,
                json=payload
            )

            if response.status_code != 200:
                logger.error(f"Dropbox API error: {response.status_code} - {response.text}")
                return []

            data = response.json()

            # Extract only folder names
            folders = []
            for entry in data.get("entries", []):
                if entry.get(".tag") == "folder":
                    folder_name = entry.get("name")
                    if folder_name:
                        folders.append(folder_name)

            logger.info(f"Found {len(folders)} folders in '{path}': {folders}")
            return folders

    except Exception as e:
        logger.error(f"Error listing Dropbox folders: {e}")
        return []


async def folder_exists(access_token: str, folder_path: str) -> bool:
    """
    Check if a folder exists in Dropbox

    Args:
        access_token: Dropbox access token
        folder_path: Full path to check (e.g., "/Documentos/Facturas")

    Returns:
        True if folder exists, False otherwise
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "path": folder_path
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.dropboxapi.com/2/files/get_metadata",
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                data = response.json()
                return data.get(".tag") == "folder"

            return False

    except Exception as e:
        logger.error(f"Error checking folder existence: {e}")
        return False


async def get_existing_structure(access_token: str) -> Dict[str, List[str]]:
    """
    Get the existing folder structure in Dropbox /Documentos

    Args:
        access_token: Dropbox access token

    Returns:
        Dict mapping category paths to their subfolders
        Example: {
            "/Documentos/Facturas": ["2024", "2025"],
            "/Documentos/Facturas/2025": ["Acme_Corp", "Microsoft"]
        }
    """
    structure = {}

    # Common document categories to check
    categories = [
        "/Documentos/Facturas",
        "/Documentos/Contratos",
        "/Documentos/Recibos",
        "/Documentos/Nóminas",
        "/Documentos/Presupuestos",
        "/Documentos/Legal",
        "/Documentos/Certificados",
        "/Documentos/Pedidos",
        "/Documentos/Albaranes",
        "/Documentos/Otros"
    ]

    for category in categories:
        # Check if category exists
        if await folder_exists(access_token, category):
            # List folders in category (years, clients, etc.)
            folders = await list_folders_in_path(access_token, category)
            structure[category] = folders

            # For each subfolder (e.g., year), check if it has client subfolders
            for folder in folders:
                subfolder_path = f"{category}/{folder}"
                subfolders = await list_folders_in_path(access_token, subfolder_path)
                if subfolders:
                    structure[subfolder_path] = subfolders

    logger.info(f"Dropbox structure: {structure}")
    return structure
