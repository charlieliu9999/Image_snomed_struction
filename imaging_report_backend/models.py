import datetime
import uuid # For generating report IDs
from typing import List, Dict, Any, Optional

class PatientInfo:
    def __init__(self, age: str, sex: str):
        self.age = age
        self.sex = sex

    def __str__(self):
        return f"PatientInfo(Age: {self.age}, Sex: {self.sex})"

    def to_dict(self) -> dict:
        return {"age": self.age, "sex": self.sex}

    @classmethod
    def from_dict(cls, data: dict) -> 'PatientInfo':
        return cls(age=data.get("age"), sex=data.get("sex"))

class SnomedEntity:
    def __init__(self, term: str, code: str, relationships: Dict[str, Any] = None,
                 children: List['SnomedEntity'] = None, translated_term: Optional[str] = None):
        self.term = term
        self.code = code
        self.relationships = relationships if relationships is not None else {}
        self.children = children if children is not None else []
        self.translated_term = translated_term

    def __str__(self, level=0):
        display_term = f"{self.term} ({self.code})"
        if self.translated_term:
            display_term += f" [{self.translated_term}]"
        ret = "\t" * level + display_term + "\n"
        for child in self.children:
            if isinstance(child, SnomedEntity):
                ret += child.__str__(level + 1)
            else:
                ret += "\t" * (level + 1) + str(child) + "\n"
        return ret

    def __repr__(self):
        return f"SnomedEntity(term='{self.term}', code='{self.code}', children_count={len(self.children)})"

    def to_dict(self) -> dict:
        return {
            "term": self.term,
            "code": self.code,
            "translated_term": self.translated_term,
            "relationships": self.relationships,
            "children": [child.to_dict() for child in self.children] # Serialize children
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'SnomedEntity':
        return cls(
            term=data.get("term"),
            code=data.get("code"),
            translated_term=data.get("translated_term"),
            relationships=data.get("relationships", {}),
            children=[SnomedEntity.from_dict(child_data) for child_data in data.get("children", [])]
        )

class LoincTerm:
    def __init__(self, term: str, code: str, translated_term: Optional[str] = None):
        self.term = term
        self.code = code
        self.translated_term = translated_term

    def to_dict(self) -> dict:
        return {"term": self.term, "code": self.code, "translated_term": self.translated_term}

    @classmethod
    def from_dict(cls, data: dict) -> 'LoincTerm':
        return cls(term=data.get("term"), code=data.get("code"), translated_term=data.get("translated_term"))

class ImagingReport:
    def __init__(self,
                 patient_info: PatientInfo,
                 chief_complaint: str,
                 examination_requested: str,
                 imaging_findings: str,
                 diagnostic_impression: str,
                 id: Optional[str] = None, # Added id
                 snomed_entities: List[SnomedEntity] = None,
                 loinc_code: Optional[LoincTerm] = None,
                 timestamp: Optional[str] = None):
        self.id = id if id else uuid.uuid4().hex # Generate ID if not provided
        self.patient_info = patient_info
        self.chief_complaint = chief_complaint
        self.examination_requested = examination_requested
        self.imaging_findings = imaging_findings
        self.diagnostic_impression = diagnostic_impression
        self.snomed_entities = snomed_entities if snomed_entities is not None else []
        self.loinc_code = loinc_code
        self.timestamp = timestamp if timestamp is not None else datetime.datetime.now().isoformat()

    def __str__(self):
        loinc_display = "N/A"
        if self.loinc_code:
            loinc_display = f"{self.loinc_code.term} ({self.loinc_code.code})"
            if self.loinc_code.translated_term:
                loinc_display += f" [{self.loinc_code.translated_term}]"

        return (f"ImagingReport(ID: {self.id}\n"
                f"  Patient Info: {self.patient_info},\n"
                f"  Chief Complaint: {self.chief_complaint},\n"
                f"  Examination Requested: {self.examination_requested},\n"
                f"  Imaging Findings: {self.imaging_findings},\n"
                f"  Diagnostic Impression: {self.diagnostic_impression},\n"
                f"  SNOMED Entities: {[entity.term for entity in self.snomed_entities]},\n"
                f"  LOINC Code: {loinc_display},\n"
                f"  Timestamp: {self.timestamp}\n)")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "patient_info": self.patient_info.to_dict() if self.patient_info else None,
            "chief_complaint": self.chief_complaint,
            "examination_requested": self.examination_requested,
            "imaging_findings": self.imaging_findings,
            "diagnostic_impression": self.diagnostic_impression,
            "snomed_entities": [entity.to_dict() for entity in self.snomed_entities],
            "loinc_code": self.loinc_code.to_dict() if self.loinc_code else None,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ImagingReport':
        patient_info_data = data.get("patient_info")
        snomed_data = data.get("snomed_entities", [])
        loinc_data = data.get("loinc_code")

        return cls(
            id=data.get("id"),
            patient_info=PatientInfo.from_dict(patient_info_data) if patient_info_data else None,
            chief_complaint=data.get("chief_complaint"),
            examination_requested=data.get("examination_requested"),
            imaging_findings=data.get("imaging_findings"),
            diagnostic_impression=data.get("diagnostic_impression"),
            snomed_entities=[SnomedEntity.from_dict(s_data) for s_data in snomed_data],
            loinc_code=LoincTerm.from_dict(loinc_data) if loinc_data else None,
            timestamp=data.get("timestamp")
        )

# New class for API output structure
class ReportAnalysisOutput:
    def __init__(self,
                 report_id: str,
                 processing_status: str, # e.g., "PENDING", "COMPLETED", "FAILED"
                 imaging_report_details: Optional[ImagingReport] = None, # Full report details
                 snomed_analysis_tree: Optional[List[SnomedEntity]] = None, # Root nodes of the SNOMED tree
                 gemini_summary: Optional[str] = None,
                 gemini_key_findings: Optional[List[str]] = None, # Or a more structured type
                 error_message: Optional[str] = None):
        self.report_id = report_id
        self.processing_status = processing_status
        self.imaging_report_details = imaging_report_details
        self.snomed_analysis_tree = snomed_analysis_tree if snomed_analysis_tree is not None else []
        self.gemini_summary = gemini_summary
        self.gemini_key_findings = gemini_key_findings if gemini_key_findings is not None else []
        self.error_message = error_message

    def to_dict(self) -> dict:
        return {
            "report_id": self.report_id,
            "processing_status": self.processing_status,
            "imaging_report_details": self.imaging_report_details.to_dict() if self.imaging_report_details else None,
            "snomed_analysis_tree": [entity.to_dict() for entity in self.snomed_analysis_tree] if self.snomed_analysis_tree else None,
            "gemini_summary": self.gemini_summary,
            "gemini_key_findings": self.gemini_key_findings,
            "error_message": self.error_message
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ReportAnalysisOutput':
        report_details_data = data.get("imaging_report_details")
        snomed_tree_data = data.get("snomed_analysis_tree", [])

        return cls(
            report_id=data.get("report_id"),
            processing_status=data.get("processing_status"),
            imaging_report_details=ImagingReport.from_dict(report_details_data) if report_details_data else None,
            snomed_analysis_tree=[SnomedEntity.from_dict(s_data) for s_data in snomed_tree_data] if snomed_tree_data else None,
            gemini_summary=data.get("gemini_summary"),
            gemini_key_findings=data.get("gemini_key_findings"),
            error_message=data.get("error_message")
        )

# This is the old ReportAnalysis class, which might be used internally by services
# but the API will likely use ReportAnalysisOutput
class ReportAnalysis: # Kept for internal use / compatibility if needed
    def __init__(self, report: ImagingReport, gemini_analysis_summary: str,
                 structured_tree_output: str): # structured_tree_output was a string representation
        self.report = report
        self.gemini_analysis_summary = gemini_analysis_summary
        self.structured_tree_output = structured_tree_output

    def to_dict(self) -> dict:
        return {
            "report": self.report.to_dict() if self.report else None,
            "gemini_analysis_summary": self.gemini_analysis_summary,
            "structured_tree_output": self.structured_tree_output,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ReportAnalysis':
        report_data = data.get("report")
        return cls(
            report=ImagingReport.from_dict(report_data) if report_data else None,
            gemini_analysis_summary=data.get("gemini_analysis_summary"),
            structured_tree_output=data.get("structured_tree_output")
        )
