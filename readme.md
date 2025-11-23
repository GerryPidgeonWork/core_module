# Python/Tkinter Application Boilerplate

## Overview
This repository is a **production-ready boilerplate** for building robust Python desktop applications using Tkinter. It provides a solid architectural foundation, separating the **Core Framework** (utilities, connectors, base GUI) from the **Application Logic** (business rules, specific UI flows).

## Project Structure

### 1. Core Framework (`core/`)
*Contains reusable, project-agnostic utilities.*
- **`C00_set_packages.py`**: Centralized dependency management.
- **`C01_set_file_paths.py`**: Dynamic path resolution.
- **`C02_system_processes.py`**: System process management and OS detection.
- **`C03_logging_handler.py`**: Standardized logging.
- **`C04_config_loader.py`**: Safe YAML/JSON config loading.
- **`C05_error_handler.py`**: Global error handling and decorators.
- **`C06_validation_utils.py`**: Data validation utilities.
- **`C07_datetime_utils.py`**: Date and time manipulation helpers.
- **`C08_string_utils.py`**: String manipulation and formatting.
- **`C09_io_utils.py`**: File I/O operations.
- **`C10_file_backup.py`**: File backup and archiving.
- **`C11_data_processing.py`**: Data processing (Pandas/NumPy helpers).
- **`C12_data_audit.py`**: Data auditing and quality checks.
- **`C13_gui_helpers.py`**: GUI helper functions (non-widget specific).
- **`C14_snowflake_connector.py`**: Secure Snowflake connectivity.
- **`C15_sql_runner.py`**: SQL execution and script running.
- **`C16_cache_manager.py`**: Caching mechanisms.
- **`C17_web_automation.py`**: Web automation (Selenium/WebDriver).
- **`C18_parallel_executor.py`**: Parallel execution and threading.
- **`C19_api_manager.py`**: Generic API request management.
- **`C20_google_api_integration.py`**: Google API integration.

### 2. GUI Framework (`gui/`)
*Contains the visual design system and base classes.*
- **`G00a_gui_packages.py`**: Centralized GUI package imports.
- **`G01a_style_config.py`**: Centralized theme constants (colors, fonts).
- **`G01b_style_engine.py`**: TTK style engine configuration.
- **`G01c_widget_primitives.py`**: Basic widget primitives (Labels, Buttons).
- **`G01d_layout_primitives.py`**: Layout primitives (Frames, Grids).
- **`G01e_gui_base.py`**: The standard `BaseGUI` window class.
- **`G01f_demo_all_primitives.py`**: Demo of all GUI primitives.
- **`G02a_layout_utils.py`**: Advanced layout utilities.
- **`G02b_container_patterns.py`**: Reusable container patterns.
- **`G02c_form_patterns.py`**: Standard form patterns.
- **`G02d_debug_utils.py`**: GUI debugging utilities.
- **`G02e_widget_components.py`**: Composite widget components.
- **`G03a_navigation.py`**: Navigation logic (Extension Point).
- **`G03b_app_menu.py`**: Application menu construction (Extension Point).
- **`G03c_dynamic_layout_engine.py`**: Dynamic layout engine (Extension Point).
- **`G03d_app_state.py`**: Application state management (Extension Point).
- **`G03e_app_controller.py`**: Main application controller (Extension Point).

### 3. Implementation (`implementation/`)
*Place your project-specific business logic here.*
- Use this directory for scripts, data processing rules, and domain-specific classes.

### 4. Main (`main/`)
*Entry point directory.*
- Create your `main.py` here to bootstrap the application.

### 5. Auxiliary Directories
- **`binary_files/`**: Storage for executable files (e.g., WebDriver binaries).
- **`cache/`**: Temporary storage for cached data and session files.
- **`config/`**: Configuration files (YAML/JSON). *See `config.example.yaml`.*
- **`credentials/`**: Secure storage for user credentials and tokens (git-ignored).
- **`data/`**: Default location for input data files.
- **`outputs/`**: Default location for generated reports and output files.
- **`scratchpad/`**: Sandbox directory for testing snippets and temporary scripts.
- **`sql/`**: Storage for SQL query files (`.sql`).
- **`tests/`**: Unit and integration tests (pytest).

### 6. Project Root Files
- **`pyproject.toml`**: Modern Python configuration (dependencies, tools).
- **`LICENSE`**: MIT License.
- **`requirements.txt`**: Legacy dependency file (kept for compatibility).
- **`readme.md`**: Project documentation.

---

## Getting Started

### 1. Installation
Ensure you have Python 3.10+ installed.
```bash
pip install -r requirements.txt
```

### 2. Configuration
Copy the example config to create your local configuration:
1. Navigate to `config/`.
2. Copy `config.example.yaml` to `config.yaml`.
3. Edit `config.yaml` with your settings.

### 3. Create Your Application
Create a `main.py` in the root directory:

```python
from gui.G01e_gui_base import BaseGUI
from gui.G00a_gui_packages import ttk

class MyApp(BaseGUI):
    def build_widgets(self):
        ttk.Label(self.main_frame, text="Hello, World!").pack(pady=20)

if __name__ == "__main__":
    app = MyApp(title="My New Tool")
    app.mainloop()
```

### 4. Run
```bash
python main.py
```

---

## Coding Standards
- **Imports**: Always use absolute imports (e.g., `from core.C01_set_file_paths import ...`).
- **Paths**: Use `pathlib.Path` for all file operations.
- **GUI**: Use `gui.G00a_gui_packages` for Tkinter imports to ensure compatibility.
