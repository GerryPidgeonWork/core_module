
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
from core.C03_logging_handler import get_logger, log_exception
logger = get_logger(__name__)

# --- Additional project-level imports (appended below canonical block) -------------------------------
from core.C01_set_file_paths import PROJECT_ROOT, LOGS_DIR, CONFIG_DIR
from core.C04_config_loader import get_config