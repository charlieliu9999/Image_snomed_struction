import datetime

class PatientInfo:
import datetime # Ensure datetime is imported

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

from typing import List, Dict, Any # Added List, Dict, Any

class SnomedEntity:
    def __init__(self, term: str, code: str, relationships: Dict[str, Any] = None, children: List['SnomedEntity'] = None):
        self.term = term
        self.code = code
        self.relationships = relationships if relationships is not None else {}
        # Children are dynamically built by build_snomed_tree and not typically part of initial construction from simple dict
        self.children = children if children is not None else []


    def __str__(self, level=0):
        ret = "\t" * level + f"{self.term} ({self.code})\n"
        # Children are populated by build_snomed_tree, __str__ helps visualize this tree
        for child in self.children:
            if isinstance(child, SnomedEntity):
                ret += child.__str__(level + 1)
            else:
                ret += "\t" * (level + 1) + str(child) + "\n"
        return ret

    def __repr__(self):
        return f"SnomedEntity(term='{self.term}', code='{self.code}', children_count={len(self.children)})"

    def to_dict(self) -> dict:
        # Children are not directly serialized to avoid redundancy/circularity if tree is already built.
        # The flat list of snomed_entities is serialized in ImagingReport.
        # If children were to be serialized, it would be: [child.to_dict() for child in self.children]
        # but this depends on whether we save the tree or the flat list.
        # For now, assuming we save flat list and rebuild tree on load, so children are not in dict.
        return {
            "term": self.term,
            "code": self.code,
            "relationships": self.relationships,
            # "children": [child.to_dict() for child in self.children] # Avoid for now
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'SnomedEntity':
        # Children are not reconstructed here; they are built by build_snomed_tree from the flat list
        return cls(
            term=data.get("term"),
            code=data.get("code"),
            relationships=data.get("relationships", {})
        )

class LoincTerm:
    def __init__(self, term: str, code: str):
        self.term = term
        self.code = code

    def to_dict(self) -> dict:
        return {"term": self.term, "code": self.code}

    @classmethod
    def from_dict(cls, data: dict) -> 'LoincTerm':
        return cls(term=data.get("term"), code=data.get("code"))

class ImagingReport:
    def __init__(self, patient_info: PatientInfo, chief_complaint: str,
                 examination_requested: str, imaging_findings: str,
                 diagnostic_impression: str, snomed_entities: List[SnomedEntity] = None,
                 loinc_code: Optional[LoincTerm] = None, timestamp: str = None): # Changed SnomedEntity list type hint
        self.patient_info = patient_info
        self.chief_complaint = chief_complaint
        self.examination_requested = examination_requested
        self.imaging_findings = imaging_findings
        self.diagnostic_impression = diagnostic_impression
        self.snomed_entities = snomed_entities if snomed_entities is not None else []
        self.loinc_code = loinc_code
        self.timestamp = timestamp if timestamp is not None else datetime.datetime.now().isoformat()

    def __str__(self):
        return (f"ImagingReport(\n"
                f"  Patient Info: {self.patient_info},\n"
                f"  Chief Complaint: {self.chief_complaint},\n"
                f"  Examination Requested: {self.examination_requested},\n"
                f"  Imaging Findings: {self.imaging_findings},\n"
                f"  Diagnostic Impression: {self.diagnostic_impression},\n"
                f"  SNOMED Entities: {[entity.term for entity in self.snomed_entities]},\n" # Simplified __str__ for entities
                f"  LOINC Code: {self.loinc_code.term if self.loinc_code else 'N/A'},\n"
                f"  Timestamp: {self.timestamp}\n)")

    def to_dict(self) -> dict:
        return {
            "patient_info": self.patient_info.to_dict() if self.patient_info else None,
            "chief_complaint": self.chief_complaint,
            "examination_requested": self.examination_requested,
            "imaging_findings": self.imaging_findings,
            "diagnostic_impression": self.diagnostic_impression,
            "snomed_entities": [entity.to_dict() for entity in self.snomed_entities],
            "loinc_code": self.loinc_code.to_dict() if self.loinc_code else None,
            "timestamp": self.timestamp, # Already a string
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ImagingReport':
        patient_info_data = data.get("patient_info")
        snomed_data = data.get("snomed_entities", [])
        loinc_data = data.get("loinc_code")

        return cls(
            patient_info=PatientInfo.from_dict(patient_info_data) if patient_info_data else None,
            chief_complaint=data.get("chief_complaint"),
            examination_requested=data.get("examination_requested"),
            imaging_findings=data.get("imaging_findings"),
            diagnostic_impression=data.get("diagnostic_impression"),
            snomed_entities=[SnomedEntity.from_dict(s_data) for s_data in snomed_data],
            loinc_code=LoincTerm.from_dict(loinc_data) if loinc_data else None,
            timestamp=data.get("timestamp")
        )

class ReportAnalysis:
    def __init__(self, report: ImagingReport, gemini_analysis_summary: str,
                 structured_tree_output: str):
        self.report = report
        self.gemini_analysis_summary = gemini_analysis_summary
        self.structured_tree_output = structured_tree_output # This will store string representation of the tree

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
