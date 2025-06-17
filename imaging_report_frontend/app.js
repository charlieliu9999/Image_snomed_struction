const { createApp, ref, reactive, onMounted, onUnmounted } = Vue; // Destructure from global Vue object

// --- SnomedTreeNode Component Definition ---
const SnomedTreeNode = {
    name: 'SnomedTreeNode',
    props: {
        node: {
            type: Object,
            required: true
        }
    },
    template: `
        <li style="margin-left: 20px; list-style-type: disc;">
            <span>
                <strong>{{ node.term }}</strong> ({{ node.code }})
                <em v-if="node.translated_term"> - {{ node.translated_term }}</em>
            </span>
            <ul v-if="node.children && node.children.length > 0" style="padding-left: 20px; margin-top: 5px; margin-bottom: 5px;">
                <snomed-tree-node
                    v-for="child in node.children"
                    :key="child.code"
                    :node="child">
                </snomed-tree-node>
            </ul>
        </li>
    `
};

// --- ReportForm Component Definition ---
const ReportForm = {
    emits: ['submit-report'],
    setup(props, { emit }) {
        const patientInfo = reactive({ age: '', sex: 'Unknown' });
        const chiefComplaint = ref('');
        const examinationRequested = ref('');
        const imagingFindings = ref('');
        const diagnosticImpression = ref('');
        const sexOptions = ref([
            { text: 'Unknown', value: 'Unknown' }, { text: 'Male', value: 'Male' },
            { text: 'Female', value: 'Female' }, { text: 'Other', value: 'Other' }
        ]);
        const handleSubmit = () => {
            if (!examinationRequested.value.trim() || !imagingFindings.value.trim() || !diagnosticImpression.value.trim()) {
                alert('Please fill in Examination Requested, Imaging Findings, and Diagnostic Impression.');
                return;
            }
            const reportData = {
                patient_info: { ...patientInfo },
                chief_complaint: chiefComplaint.value,
                examination_requested: examinationRequested.value,
                imaging_findings: imagingFindings.value,
                diagnostic_impression: diagnosticImpression.value
            };
            emit('submit-report', reportData);
        };
        return { patientInfo, chiefComplaint, examinationRequested, imagingFindings, diagnosticImpression, sexOptions, handleSubmit };
    },
    template: `
        <form @submit.prevent="handleSubmit" style="border: 1px solid #ddd; padding: 20px; border-radius: 5px;">
            <h3>Patient Information</h3>
            <div class="form-group">
                <label for="patientAge">Patient Age:</label>
                <input type="number" id="patientAge" v-model.number="patientInfo.age" placeholder="e.g., 55">
            </div>
            <div class="form-group">
                <label for="patientSex">Patient Sex:</label>
                <select id="patientSex" v-model="patientInfo.sex">
                    <option v-for="option in sexOptions" :key="option.value" :value="option.value">{{ option.text }}</option>
                </select>
            </div>
            <h3>Report Details</h3>
            <div class="form-group">
                <label for="chiefComplaint">Chief Complaint:</label>
                <textarea id="chiefComplaint" v-model="chiefComplaint" placeholder="e.g., Persistent cough for 2 weeks"></textarea>
            </div>
            <div class="form-group">
                <label for="examinationRequested">Examination Requested: *</label>
                <input type="text" id="examinationRequested" v-model="examinationRequested" placeholder="e.g., Chest X-ray AP and Lateral">
            </div>
            <div class="form-group">
                <label for="imagingFindings">Imaging Findings: *</label>
                <textarea id="imagingFindings" v-model="imagingFindings" placeholder="Describe the findings..."></textarea>
            </div>
            <div class="form-group">
                <label for="diagnosticImpression">Diagnostic Impression: *</label>
                <textarea id="diagnosticImpression" v-model="diagnosticImpression" placeholder="State the diagnostic impression..."></textarea>
            </div>
            <button type="submit">Submit Report for Analysis</button>
        </form>
    `
};

// --- HistoryView Component Definition ---
const HistoryView = {
    emits: ['view-history-details'],
    setup(props, { emit }) {
        const historyItems = ref([]);
        const isLoadingHistory = ref(false);
        const historyError = ref('');

        const fetchHistory = async () => { // Corrected async () =>
            isLoadingHistory.value = true;
            historyError.value = '';
            try {
                // apiService is globally available
                const response = await apiService.listReports(); // Assuming this returns { reports: [...] } or similar
                // The subtask description implies apiService.listReports() returns the array directly.
                // The backend GET /reports returns a list directly.
                if (response && Array.isArray(response)) {
                    historyItems.value = response.sort((a, b) => {
                        // Sort by timestamp descending (newest first)
                        // Ensure timestamps exist and are valid dates for comparison
                        const tsA = a.imaging_report_details?.timestamp || a.timestamp; // check both locations
                        const tsB = b.imaging_report_details?.timestamp || b.timestamp;
                        const dateA = new Date(tsA || 0);
                        const dateB = new Date(tsB || 0);
                        return dateB - dateA;
                    });
                } else {
                    console.warn("History response was not an array or was empty:", response);
                    historyItems.value = [];
                }
            } catch (error) {
                console.error('Error fetching history:', error);
                historyError.value = error.message || 'Failed to load history.';
            } finally {
                isLoadingHistory.value = false;
            }
        };

        const viewDetails = (reportId) => {
            if (reportId) {
                emit('view-history-details', reportId);
            }
        };

        onMounted(() => {
            fetchHistory();
        });

        return {
            historyItems,
            isLoadingHistory,
            historyError,
            fetchHistory,
            viewDetails
        };
    },
    template: `
        <div class="history-view" style="margin-top:20px; border-top: 1px solid #eee; padding-top:20px;">
            <h3>Analysis History</h3>
            <div v-if="isLoadingHistory">Loading history...</div>
            <div v-if="historyError" class="error">{{ historyError }}</div>
            <ul v-if="!isLoadingHistory && historyItems.length > 0" style="list-style: none; padding: 0;">
                <li v-for="item in historyItems" :key="item.report_id"
                    style="border: 1px solid #ddd; padding: 10px; margin-bottom: 10px; border-radius: 4px;">
                    <p><strong>Report ID:</strong> {{ item.report_id }}</p>
                    <p><strong>Timestamp:</strong> {{ item.imaging_report_details?.timestamp || item.timestamp || 'N/A' }}</p>
                    <p><strong>Patient:</strong>
                        Age {{ item.imaging_report_details?.patient_info?.age || 'N/A' }},
                        Sex {{ item.imaging_report_details?.patient_info?.sex || 'N/A' }}
                    </p>
                    <p><strong>Exam:</strong> {{ item.imaging_report_details?.examination_requested || 'N/A' }}</p>
                    <p><strong>Status:</strong> {{ item.processing_status }}</p>
                    <button @click="viewDetails(item.report_id)"
                            v-if="item.processing_status === 'COMPLETED' || item.processing_status === 'FAILED'">
                        View Details
                    </button>
                    <span v-if="item.processing_status === 'PENDING' || item.processing_status === 'POLLING_STATUS' || item.processing_status === 'PENDING_CONFIRMED'">(Processing...)</span>
                </li>
            </ul>
            <p v-if="!isLoadingHistory && historyItems.length === 0 && !historyError">No history found.</p>
        </div>
    `
};

// --- App Component Definition ---
const App = {
    components: {
        'report-form': ReportForm,
        'snomed-tree-node': SnomedTreeNode,
        'history-view': HistoryView // Register HistoryView
    },
    setup() {
        const message = ref('Imaging Report Analysis Tool');
        const reportId = ref(null);
        const processingStatus = ref('');
        const analysisResult = reactive({ data: null });
        const errorMessage = ref('');
        const isLoading = ref(false);
        const pollingIntervalId = ref(null);
        const currentView = ref('form'); // 'form' or 'history'

        const clearPolling = () => {
            if (pollingIntervalId.value) {
                clearInterval(pollingIntervalId.value);
                pollingIntervalId.value = null;
                console.log('Polling stopped.');
            }
        };

        const startPolling = (currentReportId) => {
            clearPolling();
            if (!currentReportId) { console.error('Cannot start polling without a report ID.'); return; }
            console.log(`Starting polling for report ID: ${currentReportId}`);
            isLoading.value = true;
            processingStatus.value = 'POLLING_STATUS';
            pollingIntervalId.value = setInterval(async () => {
                try {
                    const statusResponse = await apiService.getReportStatus(currentReportId);
                    console.log('Poll response:', statusResponse);
                    if (statusResponse && statusResponse.report_id) {
                        processingStatus.value = statusResponse.processing_status;
                        reportId.value = statusResponse.report_id;
                        if (statusResponse.processing_status === 'COMPLETED') {
                            analysisResult.data = statusResponse;
                            errorMessage.value = ''; clearPolling(); isLoading.value = false;
                        } else if (statusResponse.processing_status === 'FAILED') {
                            errorMessage.value = statusResponse.error_message || 'Processing failed.';
                            analysisResult.data = null; clearPolling(); isLoading.value = false;
                        } else if (['PENDING', 'PENDING_CONFIRMED', 'POLLING_STATUS'].includes(statusResponse.processing_status)) {
                            isLoading.value = true;
                        }
                    } else {
                        errorMessage.value = 'Unexpected response during polling.'; clearPolling(); isLoading.value = false;
                    }
                } catch (error) {
                    console.error('Error during status polling:', error);
                    errorMessage.value = error.message || 'Failed to poll status.';
                    processingStatus.value = 'POLLING_FAILED'; clearPolling(); isLoading.value = false;
                }
            }, 3000);
        };

        const handleFetchAndDisplayReport = async (idToFetch) => {
            isLoading.value = true;
            errorMessage.value = '';
            analysisResult.data = null;
            processingStatus.value = 'LOADING_HISTORY_ITEM';
            reportId.value = idToFetch;

            try {
                const resultData = await apiService.getReportStatus(idToFetch);
                if (resultData) {
                    analysisResult.data = resultData;
                    processingStatus.value = resultData.processing_status;
                    if (resultData.processing_status === 'FAILED') {
                        errorMessage.value = resultData.error_message || 'Failed to load report details.';
                    }
                } else {
                    errorMessage.value = 'Could not load report details.';
                    processingStatus.value = 'FAILED'; // General failure if no data
                }
            } catch (error) {
                errorMessage.value = error.message || 'Error fetching report details.';
                processingStatus.value = 'FAILED'; // General failure on catch
            } finally {
                isLoading.value = false;
            }
        };

        const handleReportSubmission = async (formData) => {
            console.log('Report submitted from form:', formData);
            currentView.value = 'form'; // Ensure form view is active
            clearPolling();
            isLoading.value = true;
            processingStatus.value = 'SUBMITTING';
            errorMessage.value = '';
            analysisResult.data = null;
            reportId.value = null;
            try {
                const responseData = await apiService.submitReport(formData);
                if (responseData && responseData.report_id) {
                    reportId.value = responseData.report_id;
                    console.log('Report submission successful. Report ID:', responseData.report_id);
                    startPolling(reportId.value);
                } else {
                    console.error('Submission response missing report_id:', responseData);
                    errorMessage.value = 'Submission successful but no report ID received.';
                    processingStatus.value = 'FAILED_SUBMISSION';
                    isLoading.value = false;
                }
            } catch (error) {
                console.error('Error during report submission:', error);
                errorMessage.value = error.message || 'Failed to submit report. Please try again.';
                processingStatus.value = 'FAILED_SUBMISSION';
                isLoading.value = false;
            }
        };

        const showFormView = () => {
            currentView.value = 'form';
        };

        const showHistoryView = () => {
            clearPolling();
            currentView.value = 'history';
        };

        const handleViewHistoryDetails = async (idToFetch) => {
            clearPolling();
            currentView.value = 'form'; // Switch view to show details in the main form/results area
            await handleFetchAndDisplayReport(idToFetch);
        };

        onMounted(() => { console.log('App component mounted!'); });
        onUnmounted(() => { clearPolling(); });

        return {
            message, reportId, processingStatus, analysisResult, errorMessage, isLoading,
            pollingIntervalId, handleReportSubmission, currentView, showFormView, showHistoryView,
            handleViewHistoryDetails
        };
    },
    template: `
        <div>
            <header style="background-color: #007bff; color: white; padding: 10px 20px; text-align: center; border-radius: 4px;">
                <h1>{{ message }}</h1>
                <nav>
                    <button @click="showFormView" :disabled="currentView === 'form'">New Report</button>
                    <button @click="showHistoryView" :disabled="currentView === 'history'" style="margin-left: 10px;">View History</button>
                </nav>
            </header>

            <main style="margin-top: 20px;">
                <div v-if="currentView === 'form'">
                    <report-form @submit-report="handleReportSubmission"></report-form>

                    <div v-if="isLoading" class="status">
                        {{
                            processingStatus === 'SUBMITTING' ? 'Submitting report...' :
                           (processingStatus === 'POLLING_STATUS' || processingStatus === 'PENDING' || processingStatus === 'PENDING_CONFIRMED' ?
                           'Checking status for Report ID: ' + (reportId || '...') + '... (Status: ' + processingStatus + ')' :
                           (processingStatus === 'LOADING_HISTORY_ITEM' ? 'Loading report details for ' + (reportId || '...') + '...' : 'Loading...'))
                        }}
                    </div>

                    <div v-if="!isLoading && reportId && processingStatus &&
                               !['SUBMITTING', 'COMPLETED', 'FAILED', 'FAILED_SUBMISSION', 'POLLING_FAILED', 'LOADING_HISTORY_ITEM'].includes(processingStatus)"
                         class="status">
                        Report ID: {{ reportId }} | Status: {{ processingStatus }}
                    </div>
                    <div v-if="errorMessage" class="error">Error: {{ errorMessage }}</div>

                    <div v-if="analysisResult.data && (processingStatus === 'COMPLETED' || (reportId && analysisResult.data.report_id === reportId && !isLoading && (processingStatus !== 'PENDING' && processingStatus !== 'POLLING_STATUS')))" class="results">
                        <h2>Analysis Results (Report ID: {{ analysisResult.data.report_id || reportId }})</h2>
                        <div v-if="analysisResult.data.imaging_report_details">
                            <h3>Patient & Report Information</h3>
                            <p><strong>Age:</strong> {{ analysisResult.data.imaging_report_details.patient_info.age || 'N/A' }}</p>
                            <p><strong>Sex:</strong> {{ analysisResult.data.imaging_report_details.patient_info.sex || 'N/A' }}</p>
                            <p><strong>Examination Requested:</strong> {{ analysisResult.data.imaging_report_details.examination_requested || 'N/A' }}</p>
                            <div v-if="analysisResult.data.imaging_report_details.loinc_code">
                                <p><strong>LOINC Code:</strong>
                                    {{ analysisResult.data.imaging_report_details.loinc_code.term }}
                                    ({{ analysisResult.data.imaging_report_details.loinc_code.code }})
                                    <em v-if="analysisResult.data.imaging_report_details.loinc_code.translated_term">
                                        - {{ analysisResult.data.imaging_report_details.loinc_code.translated_term }}
                                    </em>
                                </p>
                            </div>
                            <p><strong>Report Timestamp:</strong> {{ analysisResult.data.imaging_report_details.timestamp || 'N/A' }}</p>
                            <h3>Reported Information</h3>
                            <div class="form-group"><label>Chief Complaint:</label><pre>{{ analysisResult.data.imaging_report_details.chief_complaint || 'N/A' }}</pre></div>
                            <div class="form-group"><label>Imaging Findings:</label><pre>{{ analysisResult.data.imaging_report_details.imaging_findings || 'N/A' }}</pre></div>
                            <div class="form-group"><label>Diagnostic Impression:</label><pre>{{ analysisResult.data.imaging_report_details.diagnostic_impression || 'N/A' }}</pre></div>
                        </div>
                        <div v-if="analysisResult.data.gemini_summary">
                            <h3>Gemini LLM Analysis</h3>
                            <div class="form-group"><label>Summary:</label><pre>{{ analysisResult.data.gemini_summary }}</pre></div>
                            <div v-if="analysisResult.data.gemini_key_findings && analysisResult.data.gemini_key_findings.length">
                                <label>Key Findings:</label>
                                <ul><li v-for="(finding, index) in analysisResult.data.gemini_key_findings" :key="index">{{ finding }}</li></ul>
                            </div>
                        </div>
                        <div v-if="analysisResult.data.snomed_analysis_tree && analysisResult.data.snomed_analysis_tree.length">
                            <h3>SNOMED CT Analysis (Tree)</h3>
                            <ul style="list-style-type: none; padding-left: 0;">
                                <snomed-tree-node v-for="rootNode in analysisResult.data.snomed_analysis_tree" :key="rootNode.code" :node="rootNode"></snomed-tree-node>
                            </ul>
                        </div>
                    </div>
                </div>

                <history-view v-if="currentView === 'history'" @view-history-details="handleViewHistoryDetails">
                </history-view>
            </main>

            <footer style="margin-top: 30px; text-align: center; font-size: 0.9em; color: #777;">
                <p>&copy; 2024 Imaging Analysis Tool</p>
            </footer>
        </div>
    `
};

// Create and mount the Vue application
const app = createApp(App);
app.mount('#app');

console.log('Vue app initialized and mounted with ReportForm, SnomedTreeNode, and HistoryView.');
