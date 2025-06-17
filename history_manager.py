import json
import os
from datetime import datetime # Correct import for datetime object
from typing import List
from models import ReportAnalysis, ImagingReport, PatientInfo, SnomedEntity, LoincTerm # Import all relevant models

HISTORY_DIR = "history_records"

def save_analysis(analysis: ReportAnalysis, history_dir: str = HISTORY_DIR) -> None:
    """
    Saves a ReportAnalysis object to a JSON file in the specified history directory.
    """
    if not os.path.exists(history_dir):
        os.makedirs(history_dir, exist_ok=True)

    analysis_dict = analysis.to_dict()

    # Ensure timestamp is a string and suitable for a filename
    report_timestamp_str = analysis.report.timestamp
    if isinstance(report_timestamp_str, datetime): # Should already be string from model
        report_timestamp_str = report_timestamp_str.isoformat()

    # Sanitize timestamp for filename
    safe_timestamp = report_timestamp_str.replace(":", "-").replace("T", "_").split(".")[0] # Basic sanitization
    filename = f"analysis_{safe_timestamp}.json"
    filepath = os.path.join(history_dir, filename)

    try:
        with open(filepath, 'w') as f:
            json.dump(analysis_dict, f, indent=4)
        print(f"Analysis saved successfully to {filepath}")
    except IOError as e:
        print(f"Error saving analysis to {filepath}: {e}")
    except TypeError as e:
        print(f"Error serializing analysis to JSON: {e}")

def load_all_analyses(history_dir: str = HISTORY_DIR) -> List[ReportAnalysis]:
    """
    Loads all ReportAnalysis objects from JSON files in the specified history directory.
    """
    if not os.path.exists(history_dir):
        print(f"History directory '{history_dir}' not found.")
        return []

    analyses: List[ReportAnalysis] = []
    for filename in os.listdir(history_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(history_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    analysis = ReportAnalysis.from_dict(data)
                    analyses.append(analysis)
                print(f"Successfully loaded analysis from {filepath}")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from {filepath}: {e}")
            except IOError as e:
                print(f"Error reading file {filepath}: {e}")
            except Exception as e: # Catch other potential errors during object reconstruction
                print(f"Error reconstructing analysis from {filepath}: {e}")

    return analyses
