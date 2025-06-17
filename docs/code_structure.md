# Code Structure Overview

This document provides a high-level overview of the code structure for both the backend and frontend components of the Imaging Report Analysis Tool.

## Backend (`imaging_report_backend/`)

The backend is a Python Flask application responsible for processing requests, interacting with external medical terminologies and AI services, and managing data persistence.

Key files and directories:

*   **`app.py`**:
    *   The main entry point for the Flask application.
    *   Initializes the Flask app.
    *   Registers API blueprints.
    *   May contain basic routes (e.g., a root `/` health check).
    *   Configures and runs the Flask development server when executed directly (`python app.py`).

*   **`models.py`**:
    *   Defines the core data structures (Python classes) used throughout the backend, such as:
        *   `PatientInfo`: Stores patient demographic data.
        *   `LoincTerm`: Represents a LOINC code and its terms.
        *   `SnomedEntity`: Represents a SNOMED CT concept, its code, terms, and relationships (for tree building).
        *   `ImagingReport`: Encapsulates all data related to a single input imaging report.
        *   `ReportAnalysisOutput`: Structures the final output for API responses, including the original report details, LOINC info, SNOMED tree, and Gemini analysis.
    *   These classes include `to_dict()` and `from_dict()` methods for easy serialization and deserialization, particularly for JSON conversion for API I/O and history storage.

*   **`requirements.txt`**:
    *   Lists all Python package dependencies for the backend (e.g., Flask, requests, google-cloud-translate, google-generativeai).
    *   Used for setting up the environment via `pip install -r requirements.txt`.

*   **`api/` (Directory)**:
    *   Contains Flask Blueprints that define the API routes and handlers.
    *   **`__init__.py`**: Makes the `api` directory a Python package.
    *   **`reports_api.py`**: Defines routes related to report processing, such as:
        *   `POST /api/v1/reports`: Submitting a new report.
        *   `GET /api/v1/reports/{report_id}`: Retrieving a specific report's status/analysis.
        *   `GET /api/v1/reports`: Listing all reports.
    *   **`terminology_api.py`**: Defines routes for direct terminology lookups:
        *   `GET /api/v1/terminology/loinc/search`: Searching LOINC terms.
        *   `GET /api/v1/terminology/snomed/search`: Searching SNOMED CT terms.
    *   These API handlers are responsible for request validation (basic), calling appropriate service functions, and formatting JSON responses.

*   **`services/` (Directory)**:
    *   Contains modules that encapsulate the business logic and interactions with external services or utilities.
    *   **`__init__.py`**: Makes the `services` directory a Python package.
    *   **`terminology_services.py`**:
        *   `get_loinc_code_for_examination()`: Connects to the LOINC FHIR API to find LOINC codes.
        *   `translate_term()`: Connects to the Google Translate API for translating text.
        *   `extract_snomed_entities_from_text()`: Implements the logic for identifying terms in text (currently basic NLP placeholder), translating them, querying the Snowstorm SNOMED CT API, and fetching parent relationships.
        *   `analyze_text_with_gemini()`: Connects to the Google Gemini API for text summarization and key finding extraction.
        *   These functions include fallback mechanisms to stubbed data if API credentials are not configured.
    *   **`history_manager.py`**:
        *   `save_analysis()`: Saves a `ReportAnalysisOutput` object to a JSON file in the `history_records` directory.
        *   `load_analysis()`: Loads a specific analysis by `report_id` from its JSON file.
        *   `load_all_analyses()`: Loads all saved analyses from the `history_records` directory.
    *   **`utils.py`**:
        *   `build_snomed_tree()`: Takes a flat list of `SnomedEntity` objects (with `parent_code` relationships) and organizes them into a hierarchical tree structure.

*   **`history_records/` (Directory)**:
    *   The default directory where processed report analyses are stored as JSON files.
    *   Contains a `.gitignore` file to prevent committing history files to the repository.

*   **`tests/` (Directory)**:
    *   Contains unit tests for the backend.
    *   **`test_utils.py`**: Includes unit tests for utility functions like `build_snomed_tree`.

## Frontend (`imaging_report_frontend/`)

The frontend is a single-page application (SPA) built using Vue.js 3 (loaded via CDN). It provides the user interface for interacting with the backend API. All custom JavaScript code for the Vue application is primarily within `app.js`.

Key files:

*   **`index.html`**:
    *   The main HTML file for the application.
    *   Includes Vue.js 3 from a CDN.
    *   Contains the root `div` element (e.g., `<div id="app"></div>`) where the Vue application is mounted.
    *   Includes basic CSS styles within `<style>` tags for overall layout and component appearance.
    *   Loads the necessary JavaScript files: `apiService.js` and `app.js`.

*   **`app.js`**:
    *   The core JavaScript file for the Vue application.
    *   Initializes the global Vue object (`Vue.createApp`, etc.).
    *   **Root `App` Component**: Defines the main Vue component that manages the overall application state and layout. This component includes:
        *   Template: HTML structure for the header, main content area (which switches between form/results and history views), and footer.
        *   Reactive Data: Uses Vue's Composition API (`ref`, `reactive`) to manage state such as `currentView`, `isLoading`, `reportId`, `processingStatus`, `analysisResult`, `errorMessage`.
        *   Methods: Handles report submission (`handleReportSubmission`), view switching (`showFormView`, `showHistoryView`), loading data for selected history items (`handleViewHistoryDetails`), and polling logic (`startPolling`, `clearPolling`).
        *   Lifecycle Hooks: `onMounted` for initial setup, `onUnmounted` for cleanup (e.g., clearing polling intervals).
    *   **Child Components**: Defines and registers other Vue components directly within this file for modularity:
        *   `ReportForm`: The component for the report input form. Manages form field data and emits a `submit-report` event.
        *   `SnomedTreeNode`: A recursive component used to display the hierarchical SNOMED CT analysis tree.
        *   `HistoryView`: The component for displaying the list of past analyses and allowing users to view details of a selected item.
    *   Mounts the root `App` component to the `#app` div in `index.html`.

*   **`apiService.js`**:
    *   A plain JavaScript module responsible for all communication with the backend API.
    *   Defines `API_BASE_URL` for the backend.
    *   Contains asynchronous functions (`submitReport`, `getReportStatus`, `listReports`) that use the `fetch` API to make HTTP requests to the backend.
    *   Includes basic error handling for API responses.
    *   This module is included in `index.html` before `app.js` so its functions are available to the Vue components.

This simple file structure is chosen due to the use of Vue via CDN, avoiding a complex build system for this version of the frontend.
