# Imaging Report Structuring and Analysis Tool

This project aims to provide a tool for parsing medical imaging reports, extracting structured information using terminologies like SNOMED CT and LOINC, and leveraging LLMs like Gemini for further analysis.

## Documentation

Full documentation is available in the `/docs` directory:

*   [Introduction](./docs/introduction.md)
*   [Backend Setup](./docs/backend_setup.md)
*   [API Reference](./docs/api_reference.md)
*   [Frontend Setup](./docs/frontend_setup.md)
*   [Usage Guide](./docs/usage_guide.md)
*   [Code Structure Overview](./docs/code_structure.md)
*   [Case Study](./docs/case_study.md)

## Project Components

*   **Backend:** A Python Flask application providing a REST API for report processing.
    *   Located in the `imaging_report_backend` directory.
*   **Frontend:** A Vue.js (via CDN) single-page application for user interaction.
    *   Located in the `imaging_report_frontend` directory.

## Branches

*   `main` / `master`: (Note to maintainer: define what this branch represents)
*   `real-api-backend-phase1`: Contains the backend implementation with real API integrations.
*   `frontend-development`: Contains the frontend implementation.
*   `Documentation`: Contains this documentation.
