# ====================================================================================================
# C10_file_backup.py
# ----------------------------------------------------------------------------------------------------
# Enhanced Backup Manager for CustomPythonCoreFunctions v1.0.
#
# Purpose:
#   - Create timestamped full backups and compressed backups.
#   - Store metadata (size, MD5 hash, timestamps) alongside each backup.
#   - Provide backup listing, retention, purge, and restore features.
#   - Designed to be robust, safe, and fully logged.
#
# Usage:
#   from core.C10_file_backup import (
#       create_backup,
#       create_zipped_backup,
#       list_backups,
#       purge_old_backups,
#       restore_backup,
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
from core.C00_set_packages import *

# --- Initialise module-level logger -----------------------------------------------------------------
from core.C03_logging_handler import get_logger, log_exception, init_logging
logger = get_logger(__name__)

# --- Additional project-level imports (append below this line only) ----------------------------------
from core.C01_set_file_paths import PROJECT_ROOT
from core.C06_validation_utils import validate_file_exists
from core.C07_datetime_utils import timestamp_now


# ====================================================================================================
# 3. GLOBAL CONSTANTS
# ----------------------------------------------------------------------------------------------------
BACKUP_DIR = Path(PROJECT_ROOT) / "backups"
# IMPORTANT: No directory creation at import time.


# ====================================================================================================
# 4. MD5 HASHING HELPERS
# ----------------------------------------------------------------------------------------------------
def compute_md5(file_path: Path, chunk_size: int = 65536) -> str | None:
    """
    Description:
        Computes the MD5 hash of a file by reading it in fixed-size chunks.
        Returns the hexadecimal digest string on success, or None if the hash
        cannot be computed.

    Args:
        file_path (Path): Path to the file to hash.
        chunk_size (int): Number of bytes to read per iteration when hashing.
            Defaults to 65536 (64 KiB).

    Returns:
        str | None: MD5 hexadecimal digest if hashing succeeds; otherwise
        None when an error occurs.

    Raises:
        None.

    Notes:
        - Exceptions encountered during hashing are logged via log_exception()
          and suppressed, resulting in a None return value.
        - Chunked reading avoids loading large files entirely into memory.
    """
    try:
        hasher = hashlib.md5()
        with open(file_path, "rb") as fh:
            while True:
                chunk = fh.read(chunk_size)
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as exc:
        log_exception(exc, context=f"Computing MD5 for {file_path}")
        return None


# ====================================================================================================
# 5. BACKUP CREATION
# ----------------------------------------------------------------------------------------------------
def ensure_backup_dir() -> None:
    """
    Description:
        Ensures that the backup directory exists. This function may create
        the directory lazily at runtime but is never called at import time.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Uses BACKUP_DIR.mkdir(..., exist_ok=True), so it is safe to call
          multiple times.
        - Any exceptions are logged using log_exception() and suppressed.
    """
    try:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as exc:
        log_exception(exc, context=f"Creating backup directory {BACKUP_DIR}")


def create_backup(file_path: str | Path) -> Path:
    """
    Description:
        Creates a timestamped, uncompressed backup of a single file in the
        BACKUP_DIR directory, and writes an accompanying metadata JSON file
        with size, MD5 checksum, and timestamps.

    Args:
        file_path (str | Path): Path to the original file to back up.

    Returns:
        Path: Path to the created backup file within BACKUP_DIR.

    Raises:
        Exception: Propagates any exception raised while validating the
            source file, copying the file, or writing metadata.

    Notes:
        - The backup file name uses the pattern:
              <timestamp>_<original_name>
        - Metadata is written to:
              <backup_name><original_suffix>.json
          containing fields such as original_file, backup_file, created,
          size_bytes, and md5.
    """
    try:
        file_path = Path(file_path)
        validate_file_exists(file_path)

        ensure_backup_dir()

        timestamp = timestamp_now()
        backup_path = BACKUP_DIR / f"{timestamp}_{file_path.name}"

        shutil.copy2(file_path, backup_path)
        logger.info("🧩 Backup created: %s", backup_path)

        metadata = {
            "original_file": str(file_path),
            "backup_file": str(backup_path),
            "created": timestamp,
            "size_bytes": file_path.stat().st_size,
            "md5": compute_md5(file_path),
        }

        metadata_path = backup_path.with_suffix(backup_path.suffix + ".json")
        try:
            with open(metadata_path, "w", encoding="utf-8") as fh:
                json.dump(metadata, fh, indent=4)
            logger.info("📝 Metadata written: %s", metadata_path)
        except Exception as exc:
            log_exception(exc, context=f"Writing metadata JSON {metadata_path}")

        return backup_path

    except Exception as exc:
        log_exception(exc, context="create_backup")
        raise


def create_zipped_backup(file_path: str | Path) -> Path:
    """
    Description:
        Creates a ZIP-compressed backup of a file in BACKUP_DIR and writes
        a companion metadata JSON file describing the backup.

    Args:
        file_path (str | Path): Path to the file that will be compressed
            and backed up.

    Returns:
        Path: Path to the generated ZIP file within BACKUP_DIR.

    Raises:
        Exception: Propagates any exception raised during validation,
            ZIP creation, or metadata writing.

    Notes:
        - The ZIP file name uses the pattern:
              <timestamp>_<original_stem>.zip
        - Metadata is written to:
              <zip_path>.zip.json
          and includes the original file path, backup path, type ("zip"),
          creation timestamp, size_bytes, and MD5 checksum of the original
          file.
    """
    try:
        file_path = Path(file_path)
        validate_file_exists(file_path)

        ensure_backup_dir()

        timestamp = timestamp_now()
        zip_path = BACKUP_DIR / f"{timestamp}_{file_path.stem}.zip"

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(file_path, arcname=file_path.name)

        logger.info("🧩 Compressed backup created: %s", zip_path)

        metadata = {
            "original_file": str(file_path),
            "backup_file": str(zip_path),
            "type": "zip",
            "created": timestamp,
            "size_bytes": file_path.stat().st_size,
            "md5": compute_md5(file_path),
        }

        metadata_path = zip_path.with_suffix(".zip.json")
        try:
            with open(metadata_path, "w", encoding="utf-8") as fh:
                json.dump(metadata, fh, indent=4)
            logger.info("📝 ZIP metadata written: %s", metadata_path)
        except Exception as exc:
            log_exception(exc, context=f"Writing ZIP metadata {metadata_path}")

        return zip_path

    except Exception as exc:
        log_exception(exc, context="create_zipped_backup")
        raise


# ====================================================================================================
# 6. BACKUP LISTING & RETENTION
# ----------------------------------------------------------------------------------------------------
def list_backups(original_filename: str | Path) -> List[Path]:
    """
    Description:
        Lists all backup files in BACKUP_DIR that are associated with a
        given original filename. Metadata JSON files are excluded from
        the results.

    Args:
        original_filename (str | Path): Original filename (or path) whose
            backups should be located.

    Returns:
        List[Path]: List of backup file paths, sorted in descending order
        of modification time (newest first). Returns an empty list if an
        error occurs.

    Raises:
        None.

    Notes:
        - Only backup artifacts (files that do not end with ".json") are
          returned.
        - Any exceptions are logged using log_exception() and result in
          an empty list.
    """
    try:
        ensure_backup_dir()
        target_name = Path(original_filename).name

        backups = sorted(
            (
                p
                for p in BACKUP_DIR.iterdir()
                if target_name in p.name and not p.name.endswith(".json")
            ),
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )

        logger.info("📂 Found %s backup(s) for %s", len(backups), target_name)
        return backups

    except Exception as exc:
        log_exception(exc, context="list_backups")
        return []


def purge_old_backups(original_filename: str | Path, keep_latest: int = 3) -> None:
    """
    Description:
        Purges older backup files for a given original filename, retaining
        only the most recent N backups and their metadata. Older entries
        are deleted from disk.

    Args:
        original_filename (str | Path): Original file whose backups are
            subject to retention rules.
        keep_latest (int): Number of most recent backups to retain.
            Defaults to 3.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Deletes both the backup files and their companion metadata JSON
          files, where present.
        - Any exceptions encountered during deletion are logged but do not
          halt processing of subsequent files.
    """
    try:
        backups = list_backups(original_filename)

        if len(backups) <= keep_latest:
            logger.info("Retention satisfied — %s backups kept (limit %s).", len(backups), keep_latest)
            return

        to_delete = backups[keep_latest:]

        for path in to_delete:
            meta = path.with_suffix(path.suffix + ".json")
            try:
                if meta.exists():
                    meta.unlink()
                path.unlink()
                logger.warning("🗑️  Deleted old backup: %s", path)
            except Exception as exc:
                log_exception(exc, context=f"Deleting backup {path}")

        logger.info("♻️  Purged %s old backups, retained %s.", len(to_delete), keep_latest)

    except Exception as exc:
        log_exception(exc, context="purge_old_backups")


# ====================================================================================================
# 7. RESTORE UTILITIES
# ----------------------------------------------------------------------------------------------------
def restore_backup(original_path: str | Path, backup_file: str | Path) -> bool:
    """
    Description:
        Restores a backup file (either a raw copy or a ZIP-compressed
        backup) to the specified original location.

    Args:
        original_path (str | Path): Destination path where the file should
            be restored.
        backup_file (str | Path): Path to the backup artifact (raw file or
            ZIP archive).

    Returns:
        bool: True if the restore operation completes successfully; False
        otherwise.

    Raises:
        None.

    Notes:
        - For ZIP backups, the archive must contain exactly one file; a
          ValueError is raised internally if this is not the case, and the
          failure is logged.
        - validate_file_exists() is used to ensure the backup file is
          present before restore, and any errors are logged via
          log_exception().
    """
    try:
        original_path = Path(original_path)
        backup_file = Path(backup_file)
        validate_file_exists(backup_file)

        if backup_file.suffix.lower() == ".zip":
            with zipfile.ZipFile(backup_file, "r") as zf:
                members = zf.namelist()
                if len(members) != 1:
                    raise ValueError("ZIP backup must contain exactly one file.")

                zf.extract(members[0], original_path.parent)
                extracted = original_path.parent / members[0]
                shutil.move(extracted, original_path)
        else:
            shutil.copy2(backup_file, original_path)

        logger.info("🔄 Restored %s from %s", original_path, backup_file)
        return True

    except Exception as exc:
        log_exception(exc, context=f"restore_backup for {original_path}")
        return False


# ====================================================================================================
# 8. MAIN EXECUTION (SELF-TEST)
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    """
    Description:
        Executes a sandboxed backup workflow in a temporary directory:
        create a file, create multiple backups (raw and ZIP), list backups,
        apply retention, and restore from the latest backup.

    Args:
        None.

    Returns:
        None.

    Raises:
        None.

    Notes:
        - Uses a temporary directory so that no real project files are
          affected.
        - All feedback and diagnostics are written via the logging system
          only; no print() statements are used.
    """
    init_logging(enable_console=True)
    logger.info("🔍 C10_file_backup self-test started.")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        logger.info("🧪 Temporary directory: %s", tmpdir)

        test_file = tmpdir / "sample.txt"
        test_file.write_text("Original content")

        b1 = create_backup(test_file)
        time.sleep(0.3)

        b2 = create_zipped_backup(test_file)
        time.sleep(0.3)

        b3 = create_backup(test_file)

        all_backups = list_backups(test_file)
        logger.info("Backups found: %s", all_backups)

        purge_old_backups(test_file, keep_latest=2)

        latest = list_backups(test_file)
        if latest:
            restore_backup(test_file, latest[0])
            logger.info("Restore successful from: %s", latest[0])

    logger.info("✅ C10_file_backup self-test complete.")
