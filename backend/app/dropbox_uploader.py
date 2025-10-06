"""
Dropbox file upload module - AD-6
Handles file upload to Dropbox using access token
"""
from typing import Dict
import httpx
from fastapi import HTTPException
from pathlib import Path


async def create_folder_if_not_exists(
    access_token: str,
    folder_path: str
) -> bool:
    """
    Create folder in Dropbox if it doesn't exist
    Creates all parent folders recursively

    Args:
        access_token: Dropbox access token
        folder_path: Folder path to create (e.g., "/Documentos/Facturas")

    Returns:
        bool: True if created or already exists
    """
    import json
    import logging

    logger = logging.getLogger(__name__)

    if not folder_path or folder_path == "/":
        return True

    try:
        async with httpx.AsyncClient() as client:
            # First, check if folder exists
            check_response = await client.post(
                "https://api.dropboxapi.com/2/files/get_metadata",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                },
                json={"path": folder_path}
            )

            # If folder exists, return True
            if check_response.status_code == 200:
                logger.info(f"Folder already exists: {folder_path}")
                return True

            # Create parent folders first
            parts = folder_path.strip("/").split("/")
            current_path = ""

            for part in parts:
                current_path += "/" + part

                # Check if this level exists
                check_response = await client.post(
                    "https://api.dropboxapi.com/2/files/get_metadata",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    json={"path": current_path}
                )

                if check_response.status_code != 200:
                    # Create this level
                    logger.info(f"Creating folder: {current_path}")
                    create_response = await client.post(
                        "https://api.dropboxapi.com/2/files/create_folder_v2",
                        headers={
                            "Authorization": f"Bearer {access_token}",
                            "Content-Type": "application/json"
                        },
                        json={"path": current_path, "autorename": False}
                    )

                    if create_response.status_code != 200:
                        error_data = create_response.json()
                        # Ignore "already exists" errors
                        if "path" not in error_data.get("error", {}).get(".tag", ""):
                            logger.warning(f"Could not create folder {current_path}: {error_data}")

            return True

    except Exception as e:
        # If folder creation fails, log but continue (might already exist)
        logger.warning(f"Warning: Could not create folder {folder_path}: {str(e)}")
        return False


async def upload_file_to_dropbox(
    access_token: str,
    file_path: str,
    dropbox_path: str,
    new_filename: str
) -> Dict:
    """
    Upload file to Dropbox

    Args:
        access_token: Dropbox access token
        file_path: Local file path to upload
        dropbox_path: Destination path in Dropbox (e.g., "/Documentos/Facturas")
        new_filename: New filename for the uploaded file

    Returns:
        dict: Upload result with metadata

    Raises:
        HTTPException: If upload fails
    """
    import json
    import logging

    logger = logging.getLogger(__name__)

    # Ensure folder exists
    await create_folder_if_not_exists(access_token, dropbox_path)

    # Construct full Dropbox path
    full_dropbox_path = f"{dropbox_path}/{new_filename}"

    logger.info(f"Uploading file to Dropbox: {full_dropbox_path}")

    try:
        # Read file content
        with open(file_path, 'rb') as f:
            file_content = f.read()

        # Prepare Dropbox API arguments
        # Modo "add" con autorename para evitar sobrescribir archivos existentes
        # Si el archivo existe, Dropbox agregará automáticamente un sufijo (ej: "archivo (1).pdf")
        dropbox_api_arg = json.dumps({
            "path": full_dropbox_path,
            "mode": "add",
            "autorename": True,
            "mute": False
        })

        # Upload to Dropbox using files/upload API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://content.dropboxapi.com/2/files/upload",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Dropbox-API-Arg": dropbox_api_arg,
                    "Content-Type": "application/octet-stream"
                },
                content=file_content,
                timeout=30.0
            )

            if response.status_code != 200:
                error_detail = response.text
                logger.error(f"Dropbox upload failed: {error_detail}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Dropbox upload failed: {error_detail}"
                )

            result = response.json()
            uploaded_path = result.get('path_display')
            uploaded_name = result.get('name')

            # Verificar si el archivo fue renombrado automáticamente
            if uploaded_name != new_filename:
                logger.warning(f"Archivo renombrado automáticamente: {new_filename} -> {uploaded_name}")
                logger.info(f"El archivo ya existía, se creó una nueva versión")

            logger.info(f"File uploaded successfully: {uploaded_path}")

            return {
                "success": True,
                "path": uploaded_path,
                "name": uploaded_name,
                "id": result.get("id"),
                "size": result.get("size"),
                "was_renamed": uploaded_name != new_filename
            }

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Local file not found: {file_path}"
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=408,
            detail="Upload to Dropbox timed out"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading to Dropbox: {str(e)}"
        )
