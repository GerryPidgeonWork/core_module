# ====================================================================================================
# C18_parallel_executor.py
# ----------------------------------------------------------------------------------------------------
# Provides reusable utilities for concurrent and parallel task execution.
#
# Purpose:
#   - Execute multiple tasks concurrently using threads or processes.
#   - Accelerate I/O-bound or CPU-bound operations via unified interfaces.
#   - Provide safe concurrency with full logging, error aggregation, and progress tracking.
#
# Usage:
#   from core.C18_parallel_executor import (
#       run_in_parallel,
#       run_batches,
#       chunk_tasks,
#   )
#
# Example:
#   results = run_in_parallel(fetch_url, url_list, mode="thread", max_workers=10)
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-11-10
# Project:      Core Modules (Audited)
# ====================================================================================================


# ====================================================================================================
# 1. SYSTEM IMPORTS
# ----------------------------------------------------------------------------------------------------
# These imports (sys, pathlib.Path) are required to correctly initialise the project environment,
# ensure the core library can be imported safely (including C00_set_packages.py),
# and prevent project-local paths from overriding installed site-packages.
# ----------------------------------------------------------------------------------------------------

# --- Required for dynamic path handling and safe importing of core modules ---------------------------
import sys
from pathlib import Path

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
# (None required)


# ====================================================================================================
# 3. CORE PARALLEL EXECUTION UTILITIES
# ----------------------------------------------------------------------------------------------------
def run_in_parallel(
    func,
    tasks: List[Any],
    mode: str = "thread",
    max_workers: int = 8,
    show_progress: bool = True,
) -> List[Any]:
    """
    Execute a list of tasks concurrently using threads or processes.

    Description:
        Provides a unified wrapper around ThreadPoolExecutor and ProcessPoolExecutor.
        Returns results in order of task completion, with failed tasks returning None.

    Args:
        func (callable):
            Function to execute per task.
        tasks (List[Any]):
            Sequence of inputs to pass to func.
        mode (str):
            'thread' for I/O-bound tasks, 'process' for CPU-heavy workloads.
        max_workers (int):
            Maximum number of worker threads/processes.
        show_progress (bool):
            Whether to display tqdm progress (thread-safe).

    Returns:
        List[Any]:
            Completed task results, with None for failures.

    Raises:
        None.

    Notes:
        Executor type is chosen automatically by mode.
    """
    if not callable(func):
        logger.error("❌ Provided function is not callable.")
        return []

    executor_class = ThreadPoolExecutor if mode == "thread" else ProcessPoolExecutor
    logger.info(
        "⚙️  Executing %s tasks in %s mode (%s workers)...",
        len(tasks), mode, max_workers
    )

    results: List[Any] = []

    try:
        with executor_class(max_workers=max_workers) as executor:
            futures = {executor.submit(func, t): t for t in tasks}

            iterator = as_completed(futures)
            if show_progress:
                iterator = tqdm(
                    iterator,
                    total=len(futures),
                    desc="🚀 Executing tasks",
                    unit="task",
                )

            for future in iterator:
                try:
                    results.append(future.result())
                except Exception as exc:
                    log_exception(exc, context="run_in_parallel")
                    results.append(None)

        logger.info("✅ All tasks completed.")
        return results

    except Exception as exc:
        log_exception(exc, context="run_in_parallel (executor error)")
        return []


# ====================================================================================================
# 4. BATCH HELPERS
# ----------------------------------------------------------------------------------------------------
def chunk_tasks(task_list: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into evenly sized chunks.

    Args:
        task_list (List[Any]):
            Original list of tasks.
        chunk_size (int):
            Number of tasks per chunk.

    Returns:
        List[List[Any]]:
            List of chunked task lists.

    Raises:
        None.

    Notes:
        Returns empty list if chunk_size <= 0.
    """
    if chunk_size <= 0:
        logger.error("❌ chunk_size must be > 0.")
        return []

    return [
        task_list[i:i + chunk_size]
        for i in range(0, len(task_list), chunk_size)
    ]


def run_batches(
    func,
    all_tasks: List[Any],
    chunk_size: int = 20,
    delay: float = 0.5,
) -> List[Any]:
    """
    Execute tasks in sequential batches with optional delay between batches.

    Description:
        Useful for rate-limited APIs or controlled processing.
        Each batch uses multithreading (I/O-bound operations).

    Args:
        func (callable):
            Function executed for each task.
        all_tasks (List[Any]):
            Full list of tasks.
        chunk_size (int):
            Number of tasks per batch.
        delay (float):
            Delay (seconds) between batches.

    Returns:
        List[Any]:
            Combined results across all batches.

    Raises:
        None.

    Notes:
        Uses run_in_parallel() internally.
    """
    chunks = chunk_tasks(all_tasks, chunk_size)
    results: List[Any] = []

    logger.info("🧩 Running %s batches of size %s...", len(chunks), chunk_size)

    for idx, chunk in enumerate(chunks, start=1):
        logger.info("▶️  Starting batch %s/%s...", idx, len(chunks))
        batch_result = run_in_parallel(func, chunk, mode="thread", show_progress=False)
        results.extend(batch_result)

        if idx < len(chunks):
            time.sleep(delay)

    logger.info("✅ All batches completed.")
    return results


# ====================================================================================================
# 5. MAIN EXECUTION (SELF-TEST)
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    """
    Self-test demonstrating threaded and batched execution.
    All output is via the logger.
    """
    init_logging(enable_console=True)
    logger.info("🔍 Running C18_parallel_executor self-test...")

    def mock_task(n):
        time.sleep(0.1)
        return f"Task {n} done"

    tasks = list(range(1, 11))

    threaded_results = run_in_parallel(mock_task, tasks, mode="thread", max_workers=5)
    logger.info("🧾 Thread results: %s", threaded_results)

    batched_results = run_batches(mock_task, tasks, chunk_size=3)
    logger.info("📦 Batched results: %s", batched_results)

    logger.info("✅ C18_parallel_executor self-test complete.")
