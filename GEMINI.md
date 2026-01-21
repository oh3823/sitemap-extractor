# Sitemap Extractor Project Context

## Project Overview

**Sitemap Extractor** is a lightweight Python command-line utility designed to fetch and parse XML sitemaps from websites. It extracts all URLs defined in the sitemap and outputs them to the console.

### Key Features
*   **Automatic URL Handling:** Automatically ensures the target URL has the correct scheme (`https://`) and path (`/sitemap.xml`) if omitted.
*   **Proxy Support:** Respects system proxy settings via `HTTP_PROXY` and `HTTPS_PROXY` environment variables.
*   **Standalone Executable:** Can be built into a single-file executable for Windows and Linux using PyInstaller.
*   **Resilient:** Disables insecure request warnings and handles SSL verification gracefully (`verify=False`).

## Tech Stack
*   **Language:** Python 3.13
*   **Dependencies:** `requests`, `urllib3`
*   **Build Tool:** `pyinstaller`
*   **CI/CD:** GitHub Actions

## Getting Started

### Prerequisites
*   Python 3.13+
*   pip

### Installation
1.  Clone the repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Usage (Source)
You can run the script directly with Python:

**Command Line Argument:**
```bash
python sitemap_extractor.py example.com
# OR
python sitemap_extractor.py https://www.example.com/sitemap.xml
```

**Interactive Mode:**
If no argument is provided, the script prompts for input:
```bash
python sitemap_extractor.py
# Enter domain or URL: example.com
```

### Configuration
The application checks for the following environment variables for proxy configuration:
*   `HTTP_PROXY`
*   `HTTPS_PROXY`
*   `http_proxy`
*   `https_proxy`

## Build Process

The project is configured to build standalone executables using PyInstaller.

### Local Build
To create an executable locally:
```bash
pyinstaller --onefile sitemap_extractor.py
```
The output executable will be placed in the `dist/` directory.

### CI/CD Pipeline
The project uses GitHub Actions (`.github/workflows/workflow.yml`) for automated building and releasing:
1.  **Triggers:** Push or Pull Request to `main`.
2.  **Matrix Build:** Runs on `ubuntu-latest` and `windows-latest`.
3.  **Steps:**
    *   Sets up Python 3.13.
    *   Installs dependencies from `requirements.txt`.
    *   Builds with `pyinstaller --onefile`.
    *   Renames artifacts to `sitemap_extractor_linux` and `sitemap_extractor_windows.exe`.
4.  **Release:** Automatically creates a GitHub Release tagged `v{VERSION}.{RUN_NUMBER}` (reading base version from `VERSION` file) and uploads the artifacts.

## Project Structure

*   `sitemap_extractor.py`: Main application logic.
*   `requirements.txt`: Python package dependencies.
*   `VERSION`: Base version string (used by CI for tagging).
*   `.github/workflows/workflow.yml`: CI/CD configuration.
