# Backend Setup Guide

This guide explains how to set up and run the Python Flask backend for the Imaging Report Analysis Tool. The backend provides the API used by the frontend for processing and retrieving report analyses.

## 1. Prerequisites

*   **Python:** Python 3.8 or higher is recommended.
*   **Git:** For cloning the repository (if applicable).
*   Access to a terminal or command prompt.

## 2. Location

The backend code is located in the `imaging_report_backend` directory at the root of the project.

## 3. Installation

1.  **Navigate to the backend directory:**
    ```bash
    cd imaging_report_backend
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    Install the required Python packages using the provided `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```

## 4. Environment Variables (API Keys & Credentials)

The backend integrates with several external services (LOINC, Google Translate, Google Gemini). To use these live services, you need to set up the following environment variables. If these variables are not set, the application will gracefully fall back to using stubbed data for the corresponding services, which can be useful for development or running the application without live API access.

*   **`LOINC_USERNAME`**: Your username for the LOINC FHIR API.
*   **`LOINC_PASSWORD`**: Your password for the LOINC FHIR API.
    *   *Obtaining Credentials:* Register for a free account at [loinc.org](https://loinc.org/registration/).

*   **`GOOGLE_APPLICATION_CREDENTIALS`**: The file path to your Google Cloud service account JSON key file. This key should have permissions for the Google Cloud Translation API.
    *   *Obtaining Credentials:*
        1.  Create a Google Cloud Project at [console.cloud.google.com](https://console.cloud.google.com/).
        2.  Enable the "Cloud Translation API".
        3.  Create a service account and download its JSON key file.
        4.  Set this environment variable to the *full path* of the downloaded JSON file.

*   **`GEMINI_API_KEY`**: Your API key for the Google Gemini API.
    *   *Obtaining Credentials:* Generate an API key from Google AI Studio at [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey).

**Example of setting environment variables (Linux/macOS):**
```bash
export LOINC_USERNAME="your_loinc_username"
export LOINC_PASSWORD="your_loinc_password"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/gcp-service-account-key.json"
export GEMINI_API_KEY="your_gemini_api_key"
```
**Note for Windows:** Use `set VARIABLE_NAME=value` or set them through the System Properties dialog.

## 5. Running the Backend Development Server

Once the dependencies are installed and environment variables are (optionally) set:

1.  Ensure you are in the `imaging_report_backend` directory and your virtual environment is activated.
2.  Run the Flask application:
    ```bash
    python app.py
    ```
    (This assumes your main Flask application file is `app.py` and it's configured to run the development server when executed directly).

3.  The backend API should now be running, typically at: `http://127.0.0.1:5000`. You should see output in your terminal indicating the server has started.

## 6. Fallback Behavior (No API Keys)

If you run the backend without setting the environment variables for external APIs:
*   **LOINC lookups** will return stubbed example data.
*   **Term translations** will use a basic stub (e.g., appending "(stub)" or returning predefined translations).
*   **Gemini analysis** will return predefined stubbed text.
This allows for basic testing of the application flow even without live API access.
