# Core Boilerplate v1.0 – Developer Manual

Author: Gerry Pidgeon  
Scope: `core/` modules `C00`–`C20`  
Version: Core Boilerplate v1.0 (Audited)

---

## 1. Overview

The **Core Boilerplate v1.0** library is a reusable core for all your Python
projects, providing:

- A **central import hub** for all external and shared standard-library packages.
- Strict, **side-effect-free** core utilities for paths, configuration, logging,
  validation, datetime, strings, I/O, backups, data processing & auditing.
- Integrations for **Snowflake**, **REST APIs**, **Google Drive**, **Selenium**,
  and **parallel execution**.

All modules follow:

- Locked **Section 1 / Section 2** templates.
- **No import-time side effects** (no folders/files created at import).
- **No direct external imports** – everything comes via `C00_set_packages`.
- **No names starting with `_`** (except Python magic like `__name__`).

---

## 2. Architecture Principles

### 2.1 Protected Regions (Section 1 & 2)

Every core module starts with:

- **Section 1 – SYSTEM IMPORTS**  
  Sets up `sys.path`, `Path`, `dont_write_bytecode`, etc.
- **Section 2 – PROJECT IMPORTS**  
  Imports everything via:
  - `from core.C00_set_packages import *`
  - `from core.C03_logging_handler import get_logger, log_exception, init_logging`

These sections are **immutable** across the core library.

### 2.2 Import & Dependency Rules

- No module may import external packages directly (e.g. `import pandas`) – they
  must come from `C00_set_packages`.
- Core modules must not import GUI modules; the only GUI-touching module is
  `C13_gui_helpers`, which is explicitly allowed.
- Self-tests live under `if __name__ == "__main__":` blocks and must not be
  relied on by production code.

### 2.3 Logging & Error Handling

- All logging goes through `C03_logging_handler`.
- Exceptions are recorded using `log_exception`.
- `print()` is generally forbidden in core modules, with **explicit exceptions**
  for interactive flows (Snowflake / Google OAuth / certain self-tests).

---

## 3. Module Index (C00–C20)

- [C00_set_packages.py](#c00_set_packagespy)
- [C01_set_file_paths.py](#c01_set_file_pathspy)
- [C02_system_processes.py](#c02_system_processespy)
- [C03_logging_handler.py](#c03_logging_handlerpy)
- [C04_config_loader.py](#c04_config_loaderpy)
- [C05_error_handler.py](#c05_error_handlerpy)
- [C06_validation_utils.py](#c06_validation_utilspy)
- [C07_datetime_utils.py](#c07_datetime_utilspy)
- [C08_string_utils.py](#c08_string_utilspy)
- [C09_io_utils.py](#c09_io_utilspy)
- [C10_file_backup.py](#c10_file_backuppy)
- [C11_data_processing.py](#c11_data_processingpy)
- [C12_data_audit.py](#c12_data_auditpy)
- [C13_gui_helpers.py](#c13_gui_helperspy)
- [C14_snowflake_connector.py](#c14_snowflake_connectorpy)
- [C15_sql_runner.py](#c15_sql_runnerpy)
- [C16_cache_manager.py](#c16_cache_managerpy)
- [C17_web_automation.py](#c17_web_automationpy)
- [C18_parallel_executor.py](#c18_parallel_executorpy)
- [C19_api_manager.py](#c19_api_managerpy)
- [C20_google_api_integration.py](#c20_google_api_integrationpy)

Each module section below lists **all top-level functions and classes** as
discovered by AST parsing in Scan 2.

---

## 4. Module Reference

### C00_set_packages.py

**Role:**  
Centralised import hub for all external and shared standard-library packages.
Every other core module imports from here rather than importing packages
directly.

**Public API:**  
This module defines **no functions or classes**. It only exposes imported names.

---

### C01_set_file_paths.py

**Role:**  
Safe, centralised path handling: building project paths, managing shared-drive
roots, and temp file creation.

**Functions**

| Name                         | Type     |
|------------------------------|----------|
| `ensure_directory`           | function |
| `build_path`                 | function |
| `get_temp_file`              | function |
| `normalise_shared_drive_root`| function |
| `path_exists_safely`         | function |

---

### C02_system_processes.py

**Role:**  
OS / environment helpers for detecting the OS and user-level folders.

**Functions**

| Name                  | Type     |
|-----------------------|----------|
| `detect_os`           | function |
| `user_download_folder`| function |

---

### C03_logging_handler.py

**Role:**  
Central logging setup: logger configuration, print redirection, and helpers for
clean log formatting and exception capture.

**Classes**

| Name             | Type  |
|------------------|-------|
| `PrintRedirector`| class |

**Functions**

| Name                         | Type     |
|------------------------------|----------|
| `init_logging`               | function |
| `configure_logging`          | function |
| `enable_print_redirection`   | function |
| `disable_print_redirection`  | function |
| `get_logger`                 | function |
| `log_divider`                | function |
| `log_exception`              | function |

---

### C04_config_loader.py

**Role:**  
Centralised configuration loader and cache (YAML/JSON), plus access helpers.

**Functions**

| Name                 | Type     |
|----------------------|----------|
| `load_yaml_config`   | function |
| `load_json_config`   | function |
| `merge_dicts`        | function |
| `initialise_config`  | function |
| `reload_config`      | function |
| `get_config`         | function |

---

### C05_error_handler.py

**Role:**  
Centralised error handling utilities and optional global exception hook.

**Functions**

| Name                          | Type     |
|-------------------------------|----------|
| `handle_error`                | function |
| `global_exception_hook`       | function |
| `install_global_exception_hook`| function|
| `simulate_error`              | function |

---

### C06_validation_utils.py

**Role:**  
Reusable validators for files, directories, data structures, and configuration.

**Functions**

| Name                       | Type     |
|----------------------------|----------|
| `validate_file_exists`     | function |
| `validate_directory_exists`| function |
| `dir_exists`               | function |
| `file_exists`              | function |
| `validate_required_columns`| function |
| `validate_non_empty`       | function |
| `validate_numeric`         | function |
| `validate_config_keys`     | function |
| `validation_report`        | function |

---

### C07_datetime_utils.py

**Role:**  
Datetime helpers for formatting, parsing, ranges, and fiscal/weekly computations.

**Functions**

| Name                 | Type     |
|----------------------|----------|
| `as_str`             | function |
| `timestamp_now`      | function |
| `get_today`          | function |
| `get_now`            | function |
| `format_date`        | function |
| `parse_date`         | function |
| `get_start_of_week`  | function |
| `get_end_of_week`    | function |
| `get_week_range`     | function |
| `get_start_of_month` | function |
| `get_end_of_month`   | function |
| `get_month_range`    | function |
| `generate_date_range`| function |
| `is_within_range`    | function |
| `get_fiscal_quarter` | function |
| `get_week_id`        | function |

---

### C08_string_utils.py

**Role:**  
String normalisation, IDs, filenames, pattern extraction and numeric parsing.

**Classes**

| Name          | Type  |
|---------------|-------|
| `StringUtils` | class |

**Functions**

| Name                    | Type     |
|-------------------------|----------|
| `normalize_text`        | function |
| `slugify_filename`      | function |
| `make_safe_id`          | function |
| `extract_pattern`       | function |
| `clean_filename_generic`| function |
| `generate_dated_filename`| function|
| `parse_number`          | function |

---

### C09_io_utils.py

**Role:**  
File I/O helpers for CSV, JSON, Excel, and simple file appends.

**Functions**

| Name             | Type     |
|------------------|----------|
| `read_csv_file`  | function |
| `save_dataframe` | function |
| `read_json`      | function |
| `save_json`      | function |
| `save_excel`     | function |
| `get_latest_file`| function |
| `append_to_file` | function |

---

### C10_file_backup.py

**Role:**  
Backup manager for timestamped & zipped backups, metadata and restore logic.

**Functions**

| Name                 | Type     |
|----------------------|----------|
| `compute_md5`        | function |
| `ensure_backup_dir`  | function |
| `create_backup`      | function |
| `create_zipped_backup`| function|
| `list_backups`       | function |
| `purge_old_backups`  | function |
| `restore_backup`     | function |

---

### C11_data_processing.py

**Role:**  
General data processing utilities for DataFrames: transforms, cleaning, merging.

**Functions**

| Name                 | Type     |
|----------------------|----------|
| `standardise_columns`| function |
| `convert_to_datetime`| function |
| `fill_missing`       | function |
| `remove_duplicates`  | function |
| `filter_rows`        | function |
| `merge_dataframes`   | function |
| `summarise_numeric`  | function |

---

### C12_data_audit.py

**Role:**  
Data comparison and auditing helpers to highlight differences and reconcile totals.

**Functions**

| Name                    | Type     |
|-------------------------|----------|
| `get_missing_rows`      | function |
| `compare_dataframes`    | function |
| `reconcile_column_sums` | function |
| `summarise_differences` | function |
| `log_audit_summary`     | function |

---

### C13_gui_helpers.py

**Role:**  
Thin helpers that bridge core to GUI environments (Tkinter popups + threaded work).

**Classes**

| Name           | Type  |
|----------------|-------|
| `ProgressPopup`| class |

**Functions**

| Name         | Type     |
|--------------|----------|
| `show_info`  | function |
| `show_warning`| function|
| `show_error` | function |
| `run_in_thread`| function|

---

### C14_snowflake_connector.py

**Role:**  
Snowflake + Okta SSO integration with automatic context selection and a query helper.

**Functions**

| Name                     | Type     |
|--------------------------|----------|
| `get_snowflake_credentials`| function|
| `set_snowflake_context`  | function |
| `connect_to_snowflake`   | function |
| `run_query`              | function |

---

### C15_sql_runner.py

**Role:**  
Loads `.sql` files from the `sql/` folder, applies parameters, and executes via
the Snowflake connector.

**Functions**

| Name           | Type     |
|----------------|----------|
| `load_sql_file`| function |
| `run_sql_file` | function |

---

### C16_cache_manager.py

**Role:**  
Lightweight cache layer for JSON, CSV (DataFrames), and pickle objects.

**Functions**

| Name            | Type     |
|-----------------|----------|
| `ensure_cache_dir`| function|
| `get_cache_path` | function |
| `save_cache`     | function |
| `load_cache`     | function |
| `clear_cache`    | function |
| `list_cache_files`| function|

---

### C17_web_automation.py

**Role:**  
Selenium Chrome WebDriver helpers for browser automation.

**Functions**

| Name             | Type     |
|------------------|----------|
| `get_chrome_driver` | function |
| `wait_for_element`  | function |
| `scroll_to_bottom`  | function |
| `click_element`     | function |
| `close_driver`      | function |

---

### C18_parallel_executor.py

**Role:**  
Simple, reusable interfaces around `ThreadPoolExecutor` / `ProcessPoolExecutor`
for concurrent or batched work.

**Functions**

| Name           | Type     |
|----------------|----------|
| `run_in_parallel`| function|
| `chunk_tasks`   | function |
| `run_batches`   | function |

---

### C19_api_manager.py

**Role:**  
Standardised HTTP request helpers with retries, timeouts, and JSON parsing.

**Functions**

| Name            | Type     |
|-----------------|----------|
| `api_request`   | function |
| `get_json`      | function |
| `post_json`     | function |
| `get_auth_header`| function|

---

### C20_google_api_integration.py

**Role:**  
Google Drive API integration (OAuth 2.0) + helpers for upload/download and
DataFrame→CSV uploads.

**Functions**

| Name                     | Type     |
|--------------------------|----------|
| `get_drive_service`      | function |
| `find_folder_id`         | function |
| `find_file_id`           | function |
| `upload_file`            | function |
| `upload_dataframe_as_csv`| function |
| `download_file`          | function |

---

## 5. Usage Guidelines

1. **Always call `init_logging()`** before heavy workloads, long-running
   processes, or anything using Snowflake / APIs / Selenium so logs are
   centralised and consistent.

2. **Use `build_path()` and `PROJECT_ROOT`** (from `C01`) rather than manual
   string concatenation for any file system paths.

3. **Validate early** with `C06_validation_utils` before committing to long-running
   operations (e.g. check required columns, file existence).

4. **Encapsulate external integrations** (Snowflake, Google, REST, Selenium) via
   the dedicated modules (`C14`, `C20`, `C19`, `C17`) and avoid project-specific
   hacks in the core.

5. **Keep the core pure:**  
   New functionality should be generic and broadly reusable. Anything specific to
   a project should live in implementation (`Ixx`) modules and call into core.