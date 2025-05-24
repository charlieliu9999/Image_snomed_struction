from models import ImagingReport, PatientInfo, SnomedEntity, LoincTerm, ReportAnalysis # Added ReportAnalysis
from terminology_services import extract_snomed_entities_from_text, get_loinc_code_for_examination, translate_term, analyze_text_with_gemini
from utils import build_snomed_tree 
from history_manager import save_analysis, load_all_analyses # Import history functions
from typing import List, Optional # Added Optional for type hinting
import io # For capturing print output of the tree

def display_full_analysis(analysis: ReportAnalysis) -> None:
    """Displays a single ReportAnalysis object in a structured format."""
    
    print("\n==================================================")
    print("PATIENT AND EXAMINATION INFO")
    print("==================================================")
    if analysis.report and analysis.report.patient_info:
        print(f"Patient Age: {analysis.report.patient_info.age}")
        print(f"Patient Sex: {analysis.report.patient_info.sex}")
    else:
        print("Patient Info: N/A")
        
    if analysis.report:
        print(f"Examination Requested: {analysis.report.examination_requested}")
        translated_loinc_term = "N/A"
        if analysis.report.loinc_code:
            translated_loinc_term = translate_term(analysis.report.loinc_code.term, 'zh')
            print(f"LOINC Code: {analysis.report.loinc_code.code} - {analysis.report.loinc_code.term} [{translated_loinc_term}]")
        else:
            print(f"LOINC Code: N/A")
        print(f"Report Timestamp: {analysis.report.timestamp}")
    else:
        print("Examination Requested: N/A")
        print("LOINC Code: N/A")
        print("Report Timestamp: N/A")

    print("\n==================================================")
    print("REPORTED INFORMATION")
    print("==================================================")
    if analysis.report:
        print("Chief Complaint:")
        print(analysis.report.chief_complaint)
        print("\nImaging Findings:")
        print(analysis.report.imaging_findings)
        print("\nDiagnostic Impression:")
        print(analysis.report.diagnostic_impression)
    else:
        print("Reported information not available.")

    print("\n==================================================")
    print("SNOMED CT ANALYSIS")
    print("==================================================")
    if analysis.report and analysis.report.snomed_entities:
        print("--- Translated SNOMED Entities (Flat List) ---")
        for entity in analysis.report.snomed_entities:
            print(f"- {entity.term} ({entity.code}) - [{translate_term(entity.term, 'zh')}]")
    else:
        print("No SNOMED entities found in the report.")
    
    print("\n--- SNOMED CT Hierarchy (from Findings & Impression) ---")
    if analysis.structured_tree_output and analysis.structured_tree_output.strip():
        print(analysis.structured_tree_output)
    else:
        print("No hierarchical tree output available for SNOMED entities.")
        
    print("\n==================================================")
    print("GEMINI LLM ANALYSIS")
    print("==================================================")
    print("Summary:")
    print(analysis.gemini_analysis_summary if analysis.gemini_analysis_summary else "N/A")
    # Placeholder for other Gemini outputs if they were part of ReportAnalysis
    # For example, if Gemini generated structured key findings directly:
    # if hasattr(analysis, 'gemini_structured_findings') and analysis.gemini_structured_findings:
    #     print("\nKey Findings (from Gemini):")
    #     print(analysis.gemini_structured_findings) # Assuming this is a pre-formatted string or dict
    print("==================================================\n")


def get_report_from_cli_input() -> ImagingReport:
    """Prompts the user for imaging report details and returns an ImagingReport object."""
    print("Please enter the following details for the imaging report:")

    patient_age = input("Patient Age: ")
    patient_sex = input("Patient Sex (Male/Female/Other): ")
    chief_complaint = input("Chief Complaint: ")
    examination_requested = input("Examination Requested: ")

    print("Imaging Findings (type 'END' on a new line when done):")
    imaging_findings_lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        imaging_findings_lines.append(line)
    imaging_findings = "\n".join(imaging_findings_lines)

    print("Diagnostic Impression (type 'END' on a new line when done):")
    diagnostic_impression_lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        diagnostic_impression_lines.append(line)
    diagnostic_impression = "\n".join(diagnostic_impression_lines)

    patient_info = PatientInfo(age=patient_age, sex=patient_sex)
    imaging_report = ImagingReport(
        patient_info=patient_info,
        chief_complaint=chief_complaint,
        examination_requested=examination_requested,
        imaging_findings=imaging_findings,
        diagnostic_impression=diagnostic_impression
    )
    return imaging_report

if __name__ == "__main__":
    print("Starting Imaging Report Input...")
    report = get_report_from_cli_input()
    print("\n--- Generated Imaging Report ---")
    print(report)
    print("--- End of Report ---")

    print("\n--- Terminology Analysis ---")
    # Analyze imaging findings
    print("\nAnalyzing Imaging Findings for SNOMED entities:")
    flat_snomed_entities_findings: List[SnomedEntity] = extract_snomed_entities_from_text(report.imaging_findings)
    if flat_snomed_entities_findings:
        print("  Raw SNOMED Entities (Findings):")
        for entity in flat_snomed_entities_findings:
            # Temporarily using repr or a simple print for raw entities before tree
            print(f"    - {entity.term} ({entity.code}), Relationships: {entity.relationships}")
            # translated_term = translate_term(entity.term, target_language="zh") # Translation can be done after tree if needed
            # print(f"    Chinese Translation: {translated_term}")
        
        print("\n  SNOMED Entity Tree (Findings):")
        snomed_tree_findings: List[SnomedEntity] = build_snomed_tree(flat_snomed_entities_findings)
        if snomed_tree_findings:
            for root_node in snomed_tree_findings:
                print(root_node) # This will use the __str__ method from SnomedEntity
                # Example of translating terms in the tree (can be more sophisticated)
                # for child_entity in root_node.children: # and recursively
                #    child_entity.term = translate_term(child_entity.term, target_language="zh")
                # print(root_node) # Print again if you want to see translated tree
        else:
            print("    No tree structure could be built or no root nodes found.")
    else:
        print("  No SNOMED entities found in imaging findings.")

    # Analyze diagnostic impression
    print("\nAnalyzing Diagnostic Impression for SNOMED entities:")
    flat_snomed_entities_impression: List[SnomedEntity] = extract_snomed_entities_from_text(report.diagnostic_impression)
    if flat_snomed_entities_impression:
        print("  Raw SNOMED Entities (Impression):")
        for entity in flat_snomed_entities_impression:
            print(f"    - {entity.term} ({entity.code}), Relationships: {entity.relationships}")

        print("\n  SNOMED Entity Tree (Impression):")
        snomed_tree_impression: List[SnomedEntity] = build_snomed_tree(flat_snomed_entities_impression)
        if snomed_tree_impression:
            for root_node in snomed_tree_impression:
                print(root_node) # This will use the __str__ method
        else:
            print("    No tree structure could be built or no root nodes found.")
    else:
        print("  No SNOMED entities found in diagnostic impression.")

    # Get LOINC code for examination requested
    print("\nGetting LOINC code for Examination Requested:")
    loinc_code_obj: LoincTerm | None = get_loinc_code_for_examination(report.examination_requested) # Renamed for clarity
    if loinc_code_obj:
        report.loinc_code = loinc_code_obj # Assign to the report object
        print(f"  Found LOINC Code: {report.loinc_code.term} (Code: {report.loinc_code.code})")
    else:
        print("  No LOINC code found for the examination requested.")
    
    # Store flat list of SNOMED entities in the report object
    report.snomed_entities = flat_snomed_entities_findings + flat_snomed_entities_impression # Combine if needed, or handle separately

    print("\n--- Gemini Analysis ---")
    # Summarize imaging findings
    print("\nSummarizing Imaging Findings with Gemini:")
    gemini_summary = analyze_text_with_gemini(report.imaging_findings, prompt_type="summarize")
    print(f"  Gemini Summary (Findings): {gemini_summary}")

    # For demonstration, we'll use the findings tree string for structured_tree_output
    # and the general summary for gemini_analysis_summary.
    # In a real scenario, you might generate a dedicated summary for the whole report.
    
    snomed_tree_output_string = ""
    if snomed_tree_findings:
        # Capture the print output of the tree to a string
        tree_string_io = io.StringIO()
        for root_node in snomed_tree_findings:
            # Temporarily redirect stdout to capture print output of the tree
            # This is a bit of a hack for __str__; ideally __str__ returns string directly
            # or have a dedicated to_tree_string() method.
            # For now, we assume __str__ prints to stdout and we capture it.
            # A better way: snomed_tree_output_string += str(root_node)
            tree_string_io.write(str(root_node)) 
        snomed_tree_output_string = tree_string_io.getvalue()
        tree_string_io.close()
    
    # Create ReportAnalysis object
    current_analysis = ReportAnalysis(
        report=report,
        gemini_analysis_summary=gemini_summary, 
        structured_tree_output=snomed_tree_output_string 
    )
    
    # Display the full analysis of the current report
    print("\n--- Displaying Full Analysis of Current Report ---")
    display_full_analysis(current_analysis)

    # Save the analysis
    print("\n--- Saving Current Analysis ---")
    save_analysis(current_analysis)

    # Load and display summaries of all past analyses
    print("\n--- Loading Summaries of All Past Analyses ---")

    all_analyses: List[ReportAnalysis] = load_all_analyses()
    if all_analyses:
        print(f"\nFound {len(all_analyses)} historical analyses (summaries):")
        for idx, analysis_item in enumerate(all_analyses):
            print(f"--- Historical Analysis {idx + 1} Summary ---")
            if analysis_item.report:
                print(f"  Report Timestamp: {analysis_item.report.timestamp}")
                if analysis_item.report.patient_info:
                    print(f"  Patient Info: Age {analysis_item.report.patient_info.age}, Sex {analysis_item.report.patient_info.sex}")
                else:
                    print("  Patient Info: N/A")
                print(f"  Diagnostic Impression (snippet): {analysis_item.report.diagnostic_impression[:100]}...")
            else:
                print("  Report data missing for this historical analysis.")
            print(f"  Gemini Summary (snippet): {analysis_item.gemini_analysis_summary[:100]}...")
    else:
        print("No historical analyses found.")

    print("\n--- End of Processing ---")
