const API_BASE_URL = 'http://127.0.0.1:5000/api/v1'; // Assuming backend runs on port 5000

const apiService = {
    async submitReport(reportData) {
        try {
            const response = await fetch(`${API_BASE_URL}/reports`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(reportData),
            });
            if (!response.ok) {
                // Try to parse error body if server sends one
                const errorData = await response.json().catch(() => ({ message: response.statusText }));
                throw new Error(`HTTP error ${response.status}: ${errorData.message || response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error submitting report:', error);
            throw error; // Re-throw to be caught by calling function
        }
    },

    async getReportStatus(reportId) {
        try {
            const response = await fetch(`${API_BASE_URL}/reports/${reportId}`);
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ message: response.statusText }));
                throw new Error(`HTTP error ${response.status}: ${errorData.message || response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`Error fetching report status for ID ${reportId}:`, error);
            throw error;
        }
    },

    async listReports() {
        try {
            const response = await fetch(`${API_BASE_URL}/reports`);
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ message: response.statusText }));
                throw new Error(`HTTP error ${response.status}: ${errorData.message || response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error listing reports:', error);
            throw error;
        }
    }
};

// Note: This file doesn't use Vue itself, it's plain JavaScript for API calls.
// It will be used by Vue components in app.js.
