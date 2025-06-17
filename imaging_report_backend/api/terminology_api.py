from flask import Blueprint, jsonify, request

terminology_bp = Blueprint('terminology_api', __name__)

@terminology_bp.route('/snomed/search', methods=['GET'])
def search_snomed():
    query = request.args.get('query', '')
    language_code = request.args.get('language_code', 'en')

    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    # Placeholder - in a real app, this would call a SNOMED search function from services
    # For now, keeping the SNOMED stub as it is, focus is on LOINC integration.
    dummy_snomed_results = []
    if "fracture" in query.lower():
        dummy_snomed_results = [
            {"term": "Fracture of bone", "code": "125605003", "translated_term": "骨折"},
            {"term": "Fracture of femur", "code": "71620000", "translated_term": "股骨骨折"},
        ]
    elif "pneumonia" in query.lower():
        dummy_snomed_results = [
            {"term": "Pneumonia", "code": "233604007", "translated_term": "肺炎"},
        ]

    return jsonify({
        "search_term": query, # Changed from "query" for consistency
        "language_code": language_code,
        "results": dummy_snomed_results
    }), 200

@terminology_bp.route('/loinc/search', methods=['GET'])
def search_loinc():
    query = request.args.get('query', '')

    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    # Dynamically import from the services package relative to the current file's package
    # This assumes that 'api' and 'services' are sibling packages under 'imaging_report_backend'
    from ..services.terminology_services import get_loinc_code_for_examination

    loinc_term_object = get_loinc_code_for_examination(query)

    results_list = []
    if loinc_term_object:
        results_list.append(loinc_term_object.to_dict()) # Convert LoincTerm object to dict

    return jsonify({
        "search_term": query,
        "results": results_list # Return a list, even if it's one item or empty
    }), 200
