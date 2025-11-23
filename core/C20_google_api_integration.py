# ====================================================================================================
# C20_google_api_integration.py
# ----------------------------------------------------------------------------------------------------
# Provides Google Drive API authentication and file operations.
#
# Purpose:
#   - Authenticate with the Google Drive API using OAuth 2.0.
#   - Upload, download, search, and list files on Google Drive.
#   - Allow uploading Pandas DataFrames directly from memory as CSV.
#
# Usage:
#   from core.C20_google_api_integration import (
#       get_drive_service,
#       find_folder_id,
#       find_file_id,
#       upload_file,
#       upload_dataframe_as_csv,
#       download_file,
#   )
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-11-18
# Project:      Core Modules (Audited)
# ====================================================================================================


# ====================================================================================================
# 1. SYSTEM IMPORTS
# ----------------------------------------------------------------------------------------------------
# These imports (sys, pathlib.Path) are required to correctly initialise the project environment,
# ensure the core library can be imported safely (including C00_set_packages.py),
# and prevent project-local paths from overriding installed site-packages.
# ----------------------------------------------------------------------------------------------------

# --- Future behaviour & type system enhancements -----------------------------------------------------
from __future__ import annotations           # Future-proof type hinting (PEP 563 / PEP 649)

# --- Required for dynamic path handling and safe importing of core modules ---------------------------
import sys                                   # Python interpreter access (path, environment, runtime)
from pathlib import Path                     # Modern, object-oriented filesystem path handling

# --- Ensure project root DOES NOT override site-packages --------------------------------------------
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

# --- Remove '' (current working directory) which can shadow installed packages -----------------------
if "" in sys.path:
    sys.path.remove("")

# --- Prevent creation of __pycache__ folders ---------------------------------------------------------
sys.dont_write_bytecode = True


# ====================================================================================================
# 2. PROJECT IMPORTS
# ----------------------------------------------------------------------------------------------------
# Bring in shared external and standard-library packages from the central import hub.
#
# CRITICAL ARCHITECTURE RULE:
#   ALL external (and commonly-used standard-library) packages must be imported exclusively via:
#       from core.C00_set_packages import *
#   No other script may import external libraries directly.
#
# This module must not import any GUI packages.
# ----------------------------------------------------------------------------------------------------
from core.C00_set_packages import *

# --- Initialise module-level logger -----------------------------------------------------------------
from core.C03_logging_handler import get_logger, log_exception, init_logging
logger = get_logger(__name__)

# --- Additional project-level imports (append below this line only) ----------------------------------
from core.C01_set_file_paths import (
    PROJECT_ROOT,
    GDRIVE_CREDENTIALS_FILE,
    GDRIVE_TOKEN_FILE,
)
from core.C02_system_processes import user_download_folder
from core.C09_io_utils import MediaIoBaseDownload
# ====================================================================================================


# ====================================================================================================
# 3. CONSTANTS
# ----------------------------------------------------------------------------------------------------
SCOPES = ["https://www.googleapis.com/auth/drive"]
# ====================================================================================================


# ====================================================================================================
# 4. AUTHENTICATION
# ----------------------------------------------------------------------------------------------------
def get_drive_service():
    """
    Description:
        Authenticate with Google Drive API using OAuth 2.0.  
        Loads token from disk if valid, refreshes if expired, or launches a browser
        for first-time authentication. Returns an authenticated Drive service.

    Args:
        None.

    Returns:
        googleapiclient.discovery.Resource | None:
            The authenticated Google Drive API service, or None on failure.

    Raises:
        None.

    Notes:
        - Requires credentials/credentials.json from Google Cloud Console.
        - Writes/reads token.json for future sessions.
    """
    creds = None

    # --- Load existing token -------------------------------------------------------------------------
    if os.path.exists(GDRIVE_TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(GDRIVE_TOKEN_FILE, SCOPES)
            logger.info(f"🔑 Loaded existing token: {GDRIVE_TOKEN_FILE.name}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to load token, re-authenticating: {e}")
            creds = None

    # --- Validate or refresh token -------------------------------------------------------------------
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                logger.info("🔄 Token refreshed successfully.")
            except Exception as e:
                logger.error(f"❌ Token refresh failed: {e}")
                return None
        else:
            if not GDRIVE_CREDENTIALS_FILE.exists():
                logger.error(f"❌ Missing OAuth client secret: {GDRIVE_CREDENTIALS_FILE}")
                return None
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    GDRIVE_CREDENTIALS_FILE, SCOPES
                )
                creds = flow.run_local_server(port=0)
                logger.info("🌐 OAuth authentication completed.")
            except Exception as e:
                logger.error(f"❌ OAuth error: {e}")
                return None

        # --- Save token -------------------------------------------------------------------------------
        try:
            with open(GDRIVE_TOKEN_FILE, "w") as token:
                token.write(creds.to_json())
            logger.info(f"💾 Token saved: {GDRIVE_TOKEN_FILE.name}")
        except Exception as e:
            logger.warning(f"⚠️ Could not save token: {e}")

    # --- Build Drive service -------------------------------------------------------------------------
    try:
        service = build("drive", "v3", credentials=creds)
        logger.info("✅ Google Drive API service initialised.")
        return service
    except HttpError as e:
        logger.error(f"❌ HTTP error during service build: {e}")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")

    return None
# ====================================================================================================


# ====================================================================================================
# 5. HELPER FUNCTIONS — SEARCH
# ----------------------------------------------------------------------------------------------------
def find_folder_id(service, folder_name: str) -> str | None:
    """
    Description:
        Find the Google Drive folder ID matching a given folder name.

    Args:
        service (Resource): Active authenticated Drive service.
        folder_name (str): Name of the folder to search for.

    Returns:
        str | None: The folder ID, or None if not found.

    Raises:
        None.

    Notes:
        - Only returns the first matching folder.
    """
    if not service:
        logger.error("❌ Invalid Drive service.")
        return None

    try:
        query = (
            "mimeType='application/vnd.google-apps.folder' "
            f"and name='{folder_name}' and trashed=false"
        )
        response = service.files().list(
            q=query, fields="files(id, name)", pageSize=1
        ).execute()
        items = response.get("files", [])
        if not items:
            logger.warning(f"⚠️ Folder not found: {folder_name}")
            return None
        folder_id = items[0]["id"]
        logger.info(f"📁 Found folder '{folder_name}' (ID: {folder_id})")
        return folder_id
    except HttpError as e:
        logger.error(f"❌ Error searching for folder: {e}")
        return None


def find_file_id(service, file_name: str, in_folder_id: str | None = None) -> str | None:
    """
    Description:
        Find the Google Drive file ID for a given filename, optionally restricted to a folder.

    Args:
        service (Resource): Drive service.
        file_name (str): Name of the file.
        in_folder_id (str | None): Restrict search to a folder.

    Returns:
        str | None: File ID if found, otherwise None.

    Raises:
        None.

    Notes:
        - Ignores folders; returns only file-type items.
    """
    if not service:
        logger.error("❌ Invalid Drive service.")
        return None

    try:
        query = (
            f"name='{file_name}' and mimeType!='application/vnd.google-apps.folder' "
            "and trashed=false"
        )
        if in_folder_id:
            query += f" and '{in_folder_id}' in parents"

        response = service.files().list(
            q=query, fields="files(id, name)", pageSize=1
        ).execute()
        items = response.get("files", [])
        if not items:
            logger.warning(f"⚠️ File not found: {file_name}")
            return None
        file_id = items[0]["id"]
        logger.info(f"📄 Found file '{file_name}' (ID: {file_id})")
        return file_id
    except HttpError as e:
        logger.error(f"❌ Error searching for file: {e}")
        return None
# ====================================================================================================


# ====================================================================================================
# 6. FILE OPERATIONS
# ----------------------------------------------------------------------------------------------------
def upload_file(service, local_path: Path, folder_id: str | None = None, filename: str | None = None) -> str | None:
    """
    Description:
        Upload a local file to Google Drive.

    Args:
        service (Resource): Authenticated Drive service.
        local_path (Path): Path to the local file.
        folder_id (str | None): Target folder ID.
        filename (str | None): Optional rename on upload.

    Returns:
        str | None: The file ID of the uploaded file.

    Raises:
        None.

    Notes:
        - Supports resumable uploads.
    """
    if not service:
        logger.error("❌ Invalid Drive service.")
        return None
    if not local_path.exists():
        logger.error(f"❌ File not found: {local_path}")
        return None

    try:
        filename = filename or local_path.name
        metadata: dict[str, Any] = {"name": filename}
        if folder_id:
            metadata["parents"] = [folder_id]

        media = MediaFileUpload(local_path, resumable=True)
        upload_result = (
            service.files()
            .create(body=metadata, media_body=media, fields="id")
            .execute()
        )
        file_id = upload_result.get("id")
        logger.info(f"✅ Uploaded '{filename}' (ID: {file_id})")
        return file_id
    except HttpError as e:
        logger.error(f"❌ Upload error: {e}")
        return None


def upload_dataframe_as_csv(service, csv_buffer: io.StringIO, filename: str, folder_id: str | None = None) -> str | None:
    """
    Description:
        Upload a DataFrame as CSV directly from memory.

    Args:
        service (Resource): Drive API service.
        csv_buffer (io.StringIO): CSV buffer from DataFrame.to_csv().
        filename (str): The file name (must include '.csv').
        folder_id (str | None): Optional folder ID.

    Returns:
        str | None: Uploaded file ID.

    Raises:
        None.

    Notes:
        - Avoids writing CSVs to disk.
    """
    if not service:
        logger.error("❌ Invalid Drive service.")
        return None

    try:
        data_bytes = io.BytesIO(csv_buffer.getvalue().encode("utf-8"))
        metadata: dict[str, Any] = {"name": filename}
        if folder_id:
            metadata["parents"] = [folder_id]

        media = MediaIoBaseUpload(data_bytes, mimetype="text/csv", resumable=True)
        upload = (
            service.files()
            .create(body=metadata, media_body=media, fields="id")
            .execute()
        )
        file_id = upload.get("id")
        logger.info(f"✅ Uploaded DataFrame as '{filename}' (ID: {file_id})")
        return file_id
    except HttpError as e:
        logger.error(f"❌ Upload error: {e}")
        return None


def download_file(service, file_id: str, local_path: Path) -> None:
    """
    Description:
        Download a file from Google Drive.

    Args:
        service (Resource): Drive API service.
        file_id (str): The file ID to download.
        local_path (Path): Destination path.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Uses MediaIoBaseDownload for chunked downloading.
    """
    if not service:
        logger.error("❌ Invalid Drive service.")
        return

    try:
        local_path.parent.mkdir(parents=True, exist_ok=True)

        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False

        while not done:
            status, done = downloader.next_chunk()
            logger.info(f"⬇️ Download {int(status.progress() * 100)}%")

        with open(local_path, "wb") as out_file:
            out_file.write(fh.getbuffer())

        logger.info(f"✅ File saved to: {local_path}")
    except HttpError as e:
        logger.error(f"❌ Download error: {e}")
# ====================================================================================================


# ====================================================================================================
# 7. SELF TEST
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    """
    Description:
        Standalone smoke test for authentication and simple listing.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Requires valid credentials and user approval.
    """
    init_logging(enable_console=True)
    logger.info("🔍 Running C20_google_api_integration self-test...")

    service = get_drive_service()
    if service:
        try:
            results = service.files().list(
                pageSize=5, fields="files(id, name)"
            ).execute()
            files = results.get("files", [])
            if not files:
                logger.warning("⚠️ No files found.")
            else:
                for f in files:
                    logger.info(f"📄 {f['name']} (ID: {f['id']})")
        except Exception as e:
            logger.error(f"❌ Listing error: {e}")

    logger.info("✅ Google Drive API self-test complete.")
