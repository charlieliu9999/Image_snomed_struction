# Frontend Setup Guide

This guide explains how to set up and run the Vue.js frontend for the Imaging Report Analysis Tool. The frontend provides the user interface for interacting with the backend API to submit reports, view analysis results, and browse history.

## 1. Overview

The frontend is a single-page application (SPA) built using Vue.js 3. It is designed to be simple to run, loading Vue.js directly from a CDN (Content Delivery Network) and using plain HTML, CSS, and JavaScript files. This means no complex Node.js build process is required to get started.

## 2. Location

The frontend code is located in the `imaging_report_frontend` directory at the root of the project.

## 3. Prerequisites

*   **A modern web browser:** Such as Chrome, Firefox, Safari, or Edge.
*   **Backend API Running:** The frontend communicates with the backend API. Ensure the backend server is running (see [Backend Setup Guide](./backend_setup.md)) before starting the frontend. By default, the frontend expects the backend to be available at `http://127.0.0.1:5000`.

## 4. Running the Frontend

There are two main ways to run the frontend:

### Method 1: Directly Opening `index.html` (Simple)

1.  Navigate to the `imaging_report_frontend` directory in your file explorer.
2.  Double-click the `index.html` file, or right-click and choose "Open with" your preferred web browser.

*   **Note:** While this is the simplest method, some browsers may impose security restrictions on `file:///` URLs making API calls to `http://127.0.0.1:5000` (this is known as a CORS issue). If you encounter problems with API requests (e.g., reports not submitting or history not loading), try Method 2.

### Method 2: Using a Simple HTTP Server (Recommended for Development)

Using a lightweight local HTTP server can help avoid potential CORS issues and more closely mimics a deployed environment.

1.  **Ensure you have Python installed** (Python 3.x usually comes with a simple HTTP server module). If not, other simple servers like `live-server` for Node.js can also be used.

2.  **Navigate to the frontend directory in your terminal:**
    ```bash
    cd imaging_report_frontend
    ```

3.  **Start the Python HTTP server:**
    ```bash
    # For Python 3
    python -m http.server 8080
    # Or any other available port, e.g., 8000, 8081
    ```

4.  **Open your web browser** and go to `http://127.0.0.1:8080` (or the port you chose).

*   This method generally provides a smoother development experience for SPAs that make API calls.

## 5. Configuration

*   **API Base URL:** The URL for the backend API is configured in `imaging_report_frontend/apiService.js` via the `API_BASE_URL` constant. If your backend is running on a different address or port, you may need to update this value.
    ```javascript
    const API_BASE_URL = 'http://127.0.0.1:5000/api/v1';
    ```

Once running, you should see the main interface for the Imaging Report Analysis Tool, allowing you to input report details or view history.
