from flask import Blueprint, jsonify, request
import uuid
from ..models import ImagingReport, PatientInfo, ReportAnalysisOutput # Assuming models.py is one level up or in PYTHONPATH
from ..services import history_manager # Import the history manager
from ..services.terminology_services import get_loinc_code_for_examination, extract_snomed_entities_from_text, analyze_text_with_gemini
from ..services.utils import build_snomed_tree


reports_bp = Blueprint('reports_api', __name__)

@reports_bp.route('', methods=['POST'])
def submit_report():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Bad request, no data provided"}), 400

    required_fields = ["patient_info", "chief_complaint", "examination_requested", "imaging_findings", "diagnostic_impression"]
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Bad request, missing fields: {', '.join(missing_fields)}"}), 400

    report_id = uuid.uuid4().hex

    # Create ImagingReport object from input data
    imaging_report_obj = ImagingReport(
        id=report_id,
        patient_info=PatientInfo.from_dict(data.get("patient_info", {})),
        chief_complaint=data.get("chief_complaint", ""),
        examination_requested=data.get("examination_requested", ""),
        imaging_findings=data.get("imaging_findings", ""),
        diagnostic_impression=data.get("diagnostic_impression", "")
        # snomed_entities and loinc_code will be populated during processing
    )

    # Create initial ReportAnalysisOutput with PENDING status
    initial_analysis_output = ReportAnalysisOutput(
        report_id=report_id,
        processing_status="PENDING",
        imaging_report_details=imaging_report_obj, # Store the full ImagingReport object
        snomed_analysis_tree=None,
        gemini_summary=None,
        gemini_key_findings=None,
        error_message=None
    )

    history_manager.save_analysis(initial_analysis_output)

    response_data = {
        "message": "Report accepted for processing.",
        "report_id": report_id,
        "status_check_url": f"/api/v1/reports/{report_id}"
    }
    return jsonify(response_data), 202

@reports_bp.route('/<report_id>', methods=['GET'])
def get_report_status(report_id: str):
    analysis_output = history_manager.load_analysis(report_id)

    if not analysis_output:
        return jsonify({"error": "Report not found"}), 404

    if analysis_output.processing_status == "PENDING":
        print(f"Processing PENDING report_id: {report_id}")
        try:
            # Ensure imaging_report_details is an ImagingReport object
            if not isinstance(analysis_output.imaging_report_details, ImagingReport):
                 # This might happen if it was stored as dict and not fully re-instantiated by a previous version.
                 # For safety, try to re-instantiate if it's a dict.
                if isinstance(analysis_output.imaging_report_details, dict):
                    analysis_output.imaging_report_details = ImagingReport.from_dict(analysis_output.imaging_report_details)
                else: # If it's None or some other type, we can't proceed with this logic.
                    raise ValueError("imaging_report_details is not a valid ImagingReport object or dict for PENDING report.")

            current_report = analysis_output.imaging_report_details

            # 1. LOINC Processing
            loinc_term_obj = get_loinc_code_for_examination(current_report.examination_requested)
            current_report.loinc_code = loinc_term_obj # This updates the ImagingReport instance

            # 2. SNOMED Processing (assuming Chinese for extraction as per typical use case)
            findings_text = current_report.imaging_findings
            impression_text = current_report.diagnostic_impression

            snomed_entities_findings_flat = extract_snomed_entities_from_text(findings_text, language_code="zh")
            snomed_entities_impression_flat = extract_snomed_entities_from_text(impression_text, language_code="zh")

            combined_snomed_entities_map = {entity.code: entity for entity in snomed_entities_findings_flat}
            for entity in snomed_entities_impression_flat:
                if entity.code not in combined_snomed_entities_map:
                    combined_snomed_entities_map[entity.code] = entity
            all_unique_snomed_entities_flat = list(combined_snomed_entities_map.values())

            imaging_report_data_dict["snomed_entities"] = [entity.to_dict() for entity in all_unique_snomed_entities_flat]

            snomed_tree_roots = build_snomed_tree(all_unique_snomed_entities_flat)
            report_analysis_output.snomed_analysis_tree = [root.to_dict() for root in snomed_tree_roots]

        # Gemini Analysis - using the (potentially updated) service function
        # For summary, combine findings and impression. For key findings, use impression.
        text_for_gemini_summary = f"Imaging Findings: {findings_text}\n\nDiagnostic Impression: {impression_text}"
        report_analysis_output.gemini_summary = analyze_text_with_gemini(text_for_gemini_summary, prompt_type="summarize")

        # Extract key findings from the impression section
        key_findings_str = analyze_text_with_gemini(impression_text, prompt_type="extract_key_findings")
        # Convert numbered list string to actual list of strings
        report_analysis_output.gemini_key_findings = [item.strip() for item in key_findings_str.splitlines() if item.strip() and not item.strip().startswith("Error:")]


        _processed_reports[report_id] = report_analysis_output.to_dict() # Update the "DB"

    status_code = 200 if report_analysis_output.processing_status == "COMPLETED" else 202
    return jsonify(report_analysis_output.to_dict()), status_code
        ]
        report_analysis_output.gemini_summary = "Gemini Stub: Patient presents with symptoms consistent with pneumonia, imaging shows opacity in the left lower lobe."
        report_analysis_output.gemini_key_findings = ["Opacity in left lower lobe", "Signs of inflammation"]

        _processed_reports[report_id] = report_analysis_output.to_dict() # Update the "DB"

    status_code = 200 if report_analysis_output.processing_status == "COMPLETED" else 202
    return jsonify(report_analysis_output.to_dict()), status_code


@reports_bp.route('', methods=['GET']) # Changed from '/reports'
def get_all_reports():
    # This is a simplified version for the placeholder.
    # In a real app, you'd have pagination, filtering, etc.
    # And you would return a list of ReportAnalysisOutput objects (or their summaries).

    report_summaries = []
    for report_id, report_data_dict in _processed_reports.items():
        report_summaries.append({
            "report_id": report_id,
            "processing_status": report_data_dict.get("processing_status"),
            "examination_requested": report_data_dict.get("imaging_report_details", {}).get("examination_requested", "N/A"),
            "timestamp": report_data_dict.get("imaging_report_details", {}).get("timestamp", "N/A")
        })
    return jsonify(report_summaries), 200
