# API Reference

This document provides details for the backend API endpoints of the Imaging Report Analysis Tool.
The base URL for all API v1 endpoints is `/api/v1`.

## Reports API

Handles submission, retrieval, and listing of imaging reports and their analyses.

---

### 1. Submit New Report for Processing

*   **Endpoint:** `POST /api/v1/reports`
*   **Method:** `POST`
*   **Description:** Submits a new imaging report for asynchronous processing. The system will perform SNOMED CT extraction, LOINC mapping, and Gemini LLM analysis.
*   **Request Body:** `application/json`
    ```json
    {
        "patient_info": {
            "age": "string (e.g., '55' or '55Y')",
            "sex": "string (e.g., 'Male', 'Female', 'Other', 'Unknown')"
        },
        "chief_complaint": "string (optional)",
        "examination_requested": "string (e.g., 'Chest X-ray AP and Lateral')",
        "imaging_findings": "string (the main descriptive text of findings)",
        "diagnostic_impression": "string (the conclusion or impression from the report)"
    }
    ```
*   **Responses:**
    *   **`202 Accepted`**: Report submission is accepted, and processing has started.
        ```json
        {
            "message": "Report accepted for processing.",
            "report_id": "string (unique ID for this report)",
            "status_check_url": "/api/v1/reports/{report_id}"
        }
        ```
    *   **`400 Bad Request`**: Invalid request payload (e.g., missing required fields).
        ```json
        {
            "error": "string (description of the error)"
        }
        ```
*   **Example `curl` Request:**
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{
        "patient_info": {"age": "30", "sex": "Male"},
        "chief_complaint": "Cough and fever",
        "examination_requested": "Chest X-ray AP and Lateral",
        "imaging_findings": "Lungs show patchy opacities in the lower lobe. Possible pneumonia.",
        "diagnostic_impression": "Pneumonia, recommend follow-up."
    }' http://127.0.0.1:5000/api/v1/reports
    ```

---

### 2. Get Processed Report and Analysis

*   **Endpoint:** `GET /api/v1/reports/{report_id}`
*   **Method:** `GET`
*   **Description:** Retrieves the status and results of a specific imaging report analysis. If processing is ongoing, it will indicate a "PENDING" status.
*   **Path Parameter:**
    *   `report_id` (string): The unique ID of the report (obtained from the POST response).
*   **Responses:**
    *   **`200 OK`**: Report processing is complete (either "COMPLETED" or "FAILED").
        ```json
        // See ReportAnalysisOutput structure below
        {
            "report_id": "string",
            "imaging_report_details": {
                "id": "string",
                "patient_info": { "age": "string", "sex": "string" },
                "chief_complaint": "string",
                "examination_requested": "string",
                "imaging_findings": "string",
                "diagnostic_impression": "string",
                "timestamp": "string (ISO datetime)",
                "loinc_code": {  // Changed from loinc_info for consistency with models.py
                    "term": "string",
                    "code": "string",
                    "translated_term": "string (Chinese)"
                },
                "snomed_entities": [
                    // Array of SnomedEntity objects (flat list from report details)
                    // See SnomedEntity structure below (without children for this specific part)
                ]
            },
            "snomed_analysis_tree": [
                // Array of SnomedEntity objects (recursive structure)
                // See SnomedEntity structure below (with children)
            ],
            "gemini_summary": "string",
            "gemini_key_findings": ["string"], // List of strings
            "processing_status": "string ('COMPLETED' or 'FAILED')",
            "error_message": "string (null if COMPLETED, or error details if FAILED)"
        }
        ```
    *   **`202 Accepted`**: Report processing is still "PENDING" or in an intermediate state.
        ```json
        {
            "report_id": "string",
            "processing_status": "string ('PENDING', 'POLLING_STATUS', 'PENDING_CONFIRMED')",
            "message": "Report is still being processed.",
            "imaging_report_details": { /* ... initial report data ... */ }
            // May also include partial data like imaging_report_details if available
        }
        ```
    *   **`404 Not Found`**: The specified `report_id` does not exist.
        ```json
        {
            "error": "Report not found"
        }
        ```
*   **Example `curl` Request:**
    ```bash
    # Replace {report_id} with an actual ID
    curl http://127.0.0.1:5000/api/v1/reports/{report_id}
    ```

---

### 3. List All Processed Reports (History)

*   **Endpoint:** `GET /api/v1/reports`
*   **Method:** `GET`
*   **Description:** Retrieves a list of all submitted reports and their current status/analysis.
*   **Query Parameters (Conceptual - Not yet implemented in backend logic):**
    *   `limit` (int, e.g., 10): Number of reports to return per page.
    *   `offset` (int, e.g., 0): Offset for pagination.
*   **Responses:**
    *   **`200 OK`**: Successfully retrieved the list of reports.
        ```json
        [
            // Array of ReportAnalysisOutput objects
            // See ReportAnalysisOutput structure above
        ]
        ```
        *(Note: The backend currently returns a direct list, not nested under a "reports" key or with "total_reports". This documentation reflects the actual current implementation.)*
*   **Example `curl` Request:**
    ```bash
    curl http://127.0.0.1:5000/api/v1/reports
    ```

## Terminology Search API

Provides endpoints for searching LOINC and SNOMED CT terms.

---

### 4. Search LOINC Terms

*   **Endpoint:** `GET /api/v1/terminology/loinc/search`
*   **Method:** `GET`
*   **Description:** Searches for LOINC terms based on a query string. Returns the best single match found by the service.
*   **Query Parameter:**
    *   `query` (string, required): The search term (e.g., "Chest X-ray").
*   **Responses:**
    *   **`200 OK`**: Search successful.
        ```json
        {
            "search_term": "string (the provided query)",
            "results": [
                // Array containing zero or one LOINC term object
                {
                    "code": "string (LOINC code)",
                    "term": "string (LOINC long common name)",
                    "translated_term": "string (Chinese translation, if available)"
                }
            ]
        }
        ```
*   **Example `curl` Request:**
    ```bash
    curl "http://127.0.0.1:5000/api/v1/terminology/loinc/search?query=Chest%20X-ray"
    ```

---

### 5. Search SNOMED CT Terms

*   **Endpoint:** `GET /api/v1/terminology/snomed/search`
*   **Method:** `GET`
*   **Description:** Searches for SNOMED CT terms. (Note: Current backend implementation uses stubs for this endpoint).
*   **Query Parameters:**
    *   `query` (string, required): The search term.
    *   `language_code` (string, optional, e.g., "en", "zh"): Language code for search.
*   **Responses:**
    *   **`200 OK`**: Search successful.
        ```json
        {
            "search_term": "string (the provided query)",
            "language_code": "string (the provided language_code)",
            "results": [
                // Array of SnomedEntity objects (flat, not tree, from stub)
                // See SnomedEntity structure below (children would be empty for this stub)
            ]
        }
        ```
*   **Example `curl` Request:**
    ```bash
    curl "http://127.0.0.1:5000/api/v1/terminology/snomed/search?query=Pneumonia&language_code=en"
    ```

## Common Data Structures

### `ReportAnalysisOutput`
(This structure is returned by `GET /api/v1/reports/{report_id}` and in the list from `GET /api/v1/reports`)
```json
{
    "report_id": "string",
    "processing_status": "string ('PENDING', 'PENDING_CONFIRMED', 'POLLING_STATUS', 'COMPLETED', 'FAILED')",
    "imaging_report_details": { // Instance of ImagingReport
        "id": "string",
        "patient_info": { "age": "string", "sex": "string" },
        "chief_complaint": "string",
        "examination_requested": "string",
        "imaging_findings": "string",
        "diagnostic_impression": "string",
        "timestamp": "string (ISO datetime)",
        "loinc_code": { // Instance of LoincTerm
            "term": "string",
            "code": "string",
            "translated_term": "string (Chinese)"
        },
        "snomed_entities": [ // Flat list of SnomedEntity objects from report
            {
                "code": "string",
                "term": "string (English)",
                "translated_term": "string (Chinese)",
                "relationships": {"parent_code": "string (optional)"},
                "children": [] // Typically empty in this flat list context
            }
        ]
    },
    "snomed_analysis_tree": [
        // Array of SnomedEntity objects, root nodes of the processed tree
        // SnomedEntity structure here includes populated children for hierarchy
    ],
    "gemini_summary": "string (AI-generated summary)",
    "gemini_key_findings": ["string"], // List of AI-extracted key findings
    "error_message": "string (null if not FAILED, or error details if FAILED)"
}
```

### `SnomedEntity`
(Used in `ReportAnalysisOutput.imaging_report_details.snomed_entities` as a flat list, and in `ReportAnalysisOutput.snomed_analysis_tree` as a recursive tree structure. Also used in `GET /api/v1/terminology/snomed/search` results as a flat list.)
```json
{
    "code": "string (SNOMED CT code)",
    "term": "string (Preferred term, typically English from Snowstorm)",
    "translated_term": "string (Chinese translation of the term, if available)",
    "relationships": {
        "parent_code": "string (optional, code of the parent concept)"
        // Other relationships could be added here
    },
    "children": [
        // Array of SnomedEntity objects for tree structure (recursive)
        // This is populated in the snomed_analysis_tree field.
        // For flat lists (like in snomed_entities or search results), this is typically empty.
    ]
}
```
