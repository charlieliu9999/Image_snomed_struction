from models import SnomedEntity, LoincTerm # Changed to absolute import
from typing import List, Optional, Set, Any # Added Set, Any
import requests
import os
from google.cloud import translate_v2 as google_translate_client
import json
import re
import google.generativeai as genai
from google.generativeai.types import GenerationConfig # For structured output (though not fully implemented here)
from google.api_core import exceptions as google_exceptions # For specific Gemini error handling

# Helper function to be defined before its use in extract_snomed_entities_from_text
def _fetch_snomed_parent_code(snomed_code: str) -> Optional[str]:
    if not snomed_code:
        return None

    LOOKUP_URL = "https://snowstorm.snomedtools.org/fhir/CodeSystem/$lookup"
    params = {
        "system": "http://snomed.info/sct",
        "code": snomed_code,
        "property": "parent"
    }
    try:
        print(f"Snowstorm $lookup for parent of: {snomed_code}")
        response = requests.get(LOOKUP_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "parameter" in data:
            for param in data["parameter"]:
                if param.get("name") == "parent" and "valueCode" in param:
                    parent_code = param["valueCode"]
                    print(f"  Found parent for {snomed_code}: {parent_code}")
                    return parent_code
                elif param.get("name") == "property":
                    if "part" in param:
                        prop_code = None
                        prop_value = None
                        for part_item in param["part"]:
                            if part_item.get("name") == "code" and "valueCode" in part_item:
                                prop_code = part_item["valueCode"]
                            if part_item.get("name") == "value" and "valueCode" in part_item:
                                prop_value = part_item["valueCode"]
                        if prop_code == "isA" and prop_value:
                             print(f"  Found 'isA' parent for {snomed_code}: {prop_value}")
                             return prop_value
            print(f"  No 'parent' or 'isA' property found in $lookup response for {snomed_code}")
        else:
            print(f"  No 'parameter' field in $lookup response for {snomed_code}")
    except requests.exceptions.HTTPError as e:
        print(f"Snowstorm $lookup HTTP error for {snomed_code}: {e} - Response: {response.text if 'response' in locals() else 'No response'}")
    except requests.exceptions.RequestException as e:
        print(f"Snowstorm $lookup request error for {snomed_code}: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from Snowstorm $lookup for {snomed_code}: {e} - Response: {response.text if 'response' in locals() else 'No response'}")
    return None

def extract_snomed_entities_from_text(text: str, language_code: str = "zh") -> List[SnomedEntity]:
    print(f"Attempting to extract SNOMED entities from text (lang: {language_code}): '{text[:100]}...'")
    found_entities: List[SnomedEntity] = []
    candidate_terms: List[str] = []

    if language_code.startswith("zh"):
        candidate_terms = list(set(re.findall(r'[\u4e00-\u9fff]{2,}', text)))
        print(f"  Candidate Chinese terms (raw): {candidate_terms}")
    else:
        candidate_terms = list(set(text.lower().split()))[:5]
        print(f"  Candidate non-Chinese terms (raw): {candidate_terms}")

    if not candidate_terms:
        print("  No candidate terms extracted.")
        return []

    candidate_terms = candidate_terms[:5]
    print(f"  Processing first {len(candidate_terms)} unique candidate terms: {candidate_terms}")

    SNOWSTORM_EXPAND_URL = "https://snowstorm.snomedtools.org/fhir/ValueSet/$expand"
    SNOMED_ECL_CLINICAL_FINDINGS = "<<404684003"

    for i, term_to_process in enumerate(candidate_terms):
        print(f"\n  Processing term {i+1}/{len(candidate_terms)}: '{term_to_process}'")
        english_term = term_to_process
        if language_code.startswith("zh"):
            translated_to_english = translate_term(term_to_process, target_language="en", source_language="zh")
            if not translated_to_english or translated_to_english.endswith("(未翻译 - 存根)") or translated_to_english.endswith("(翻译失败:API错误)") or translated_to_english == term_to_process: # Added check if translation returned original
                print(f"    Could not translate Chinese term '{term_to_process}' to English accurately or translation was same as input. Skipping.")
                continue
            english_term = translated_to_english
            print(f"    Translated '{term_to_process}' to English: '{english_term}'")

        if not english_term:
            continue

        params = {
            "url": f"http://snomed.info/sct?fhir_vs=ecl/{SNOMED_ECL_CLINICAL_FINDINGS}",
            "filter": english_term, "count": 1, "includeDesignations": "true"
        }
        try:
            print(f"    Querying Snowstorm ValueSet/$expand for: '{english_term}'")
            response = requests.get(SNOWSTORM_EXPAND_URL, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            if "expansion" in data and "contains" in data["expansion"]:
                for item in data["expansion"]["contains"]:
                    sct_code = item.get("code")
                    sct_display_english = item.get("display")
                    if sct_code and sct_display_english:
                        print(f"      Found SNOMED: {sct_display_english} ({sct_code})")
                        sct_display_chinese = translate_term(sct_display_english, target_language="zh", source_language="en")
                        relationships = {}
                        parent_code = _fetch_snomed_parent_code(sct_code)
                        if parent_code: relationships['parent_code'] = parent_code
                        if not any(e.code == sct_code for e in found_entities):
                            found_entities.append(SnomedEntity(
                                term=sct_display_english, code=sct_code,
                                translated_term=sct_display_chinese, relationships=relationships
                            ))
                        else: print(f"      SNOMED entity {sct_code} already added.")
                    else: print(f"      Snowstorm item lacked code or display: {item}")
            else: print(f"    No 'expansion.contains' in Snowstorm response for '{english_term}'. Response: {data}")
        except requests.exceptions.HTTPError as e: print(f"    Snowstorm ValueSet/$expand HTTP error for '{english_term}': {e} - Response: {response.text if 'response' in locals() else 'No response'}")
        except requests.exceptions.RequestException as e: print(f"    Snowstorm ValueSet/$expand request error for '{english_term}': {e}")
        except json.JSONDecodeError as e: print(f"    Error decoding JSON from Snowstorm ValueSet/$expand for '{english_term}': {e} - Response: {response.text if 'response' in locals() else 'No response'}")
    print(f"\n  Finished SNOMED extraction. Found {len(found_entities)} distinct entities.")
    return found_entities

def get_loinc_code_for_examination(examination_name: str) -> Optional[LoincTerm]:
    loinc_username = os.environ.get("LOINC_USERNAME")
    loinc_password = os.environ.get("LOINC_PASSWORD")
    if not loinc_username or not loinc_password:
        print("Warning: LOINC_USERNAME or LOINC_PASSWORD environment variables not set. Cannot query LOINC API.")
        if "chest x-ray" in examination_name.lower():
            return LoincTerm(term="Chest X-ray (Stub)", code="RID28501-Stub", translated_term=translate_term("Chest X-ray (Stub)", "zh"))
        elif "mri brain" in examination_name.lower():
            return LoincTerm(term="MRI Brain (Stub)", code="RID10330-Stub", translated_term=translate_term("MRI Brain (Stub)", "zh"))
        return None
    FHIR_URL = "https://fhir.loinc.org/ValueSet/$expand"
    params = {"url": "http://loinc.org/vs", "filter": examination_name, "count": 5, "includeDesignations": "true"}
    try:
        print(f"Querying LOINC API for: {examination_name}")
        response = requests.get(FHIR_URL, params=params, auth=(loinc_username, loinc_password), timeout=10)
        response.raise_for_status()
        data = response.json()
        if "expansion" in data and "contains" in data["expansion"] and data["expansion"]["contains"]:
            first_match = data["expansion"]["contains"][0]
            loinc_code = first_match.get("code")
            english_display = first_match.get("display")
            chinese_translation_from_loinc = None
            if "designation" in first_match:
                for designation in first_match["designation"]:
                    if designation.get("language") == "zh-CN" or designation.get("language") == "zh":
                        chinese_translation_from_loinc = designation.get("value"); break
            final_chinese_translation = chinese_translation_from_loinc if chinese_translation_from_loinc else translate_term(english_display, "zh", "en")
            if loinc_code and english_display:
                print(f"LOINC API Found: {english_display} ({loinc_code}), Chinese: {final_chinese_translation}")
                return LoincTerm(term=english_display, code=loinc_code, translated_term=final_chinese_translation)
            else: print(f"LOINC API response item lacked code or display: {first_match}")
        else: print(f"No results found in LOINC API response for '{examination_name}'. Response: {data}")
    except requests.exceptions.HTTPError as e: print(f"LOINC API HTTP error: {e} - Response: {response.text if 'response' in locals() else 'No response'}")
    except requests.exceptions.RequestException as e: print(f"LOINC API request error: {e}")
    except json.JSONDecodeError as e: print(f"Error decoding JSON from LOINC API: {e} - Response: {response.text if 'response' in locals() else 'No response'}")
    return None

def translate_term(term: str, target_language: str = "zh", source_language: Optional[str] = None) -> Optional[str]:
    if not term: return term
    google_creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if google_creds_path and os.path.exists(google_creds_path):
        try:
            client = google_translate_client.Client()
            term_to_translate = term.decode("utf-8") if isinstance(term, bytes) else term
            result = client.translate(term_to_translate, target_language=target_language, source_language=source_language or '', format_='text')
            translated_text = result['translatedText']
            detected_source = result.get('detectedSourceLanguage', 'N/A')
            print(f"Google Translate API: '{term_to_translate}' (from {detected_source}) -> '{translated_text}' (to {target_language})")
            return translated_text
        except Exception as e:
            print(f"Error during Google Translate API call: {e}. Falling back.")
            if target_language == "zh": return f"{term} (翻译失败:API错误)"
            return f"{term} (translation_failed:API_error)"
    else:
        if not google_creds_path: print("Warning: GOOGLE_APPLICATION_CREDENTIALS not set. Using stub translation.")
        else: print(f"Warning: GOOGLE_APPLICATION_CREDENTIALS file not found at '{google_creds_path}'. Using stub translation.")
        print(f"Stub (fallback): Translating term '{term}' to {target_language}")
        if target_language == "zh":
            translations = {
                "Fracture of femur": "股骨骨折 (存根)", "Pneumonia": "肺炎 (存根)", "Chest X-ray": "胸部X光 (存根)",
                "MRI Brain": "脑部MRI (存根)", "Musculoskeletal event": "肌肉骨骼事件 (存根)", "Injury": "损伤 (存根)",
                "Fracture": "骨折 (存根)", "Fracture of lower limb": "下肢骨折 (存根)", "Shaft of femur": "股骨干 (存根)",
                "Neck of femur": "股骨颈 (存根)", "Neurological finding": "神经系统发现 (存根)",
                "Pain finding": "疼痛发现 (存根)", "Headache": "头痛 (存根)",
                "Chest X-ray (Stub)": "胸部X光 (双重存根)", "MRI Brain (Stub)": "脑部MRI (双重存根)"
            }
            return translations.get(term, f"{term} (未翻译 - 存根)")
        return term

def analyze_text_with_gemini(text_to_analyze: str, prompt_type: str = "summarize") -> str:
    if not text_to_analyze:
        return "Error: No text provided for analysis (Gemini)."
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY environment variable not set. Using stubbed Gemini analysis.")
        if prompt_type == "summarize": return f"Gemini Summary STUB: Text relates to '{text_to_analyze.split()[0] if text_to_analyze else 'N/A'}'."
        elif prompt_type == "extract_key_findings": return f"Gemini Key Findings STUB: 1. Finding related to '{text_to_analyze.split()[0] if text_to_analyze else 'N/A'}'."
        elif prompt_type == "structured_output_example": return '{"key_findings_stub": ["Example finding 1"], "overall_impression_stub": "This is a stub."}'
        else: return "Error: Unknown prompt type for stubbed Gemini analysis."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name='gemini-1.5-flash-latest')
        prompts = {
            "summarize": f"Summarize the following medical text concisely, focusing on clinically relevant information and primary conclusions. The text is from an imaging report. Text: {text_to_analyze}",
            "extract_key_findings": f"Extract the key medical findings as a concise, numbered list from the following imaging report text. Each finding should be clearly stated. Text: {text_to_analyze}",
            "structured_output_example": f"Analyze the following medical text from an imaging report and provide a structured summary in JSON format. The JSON should have a 'key_findings' array (list of strings) and an 'overall_impression' string. Text: {text_to_analyze}"
        }
        selected_prompt = prompts.get(prompt_type)
        if not selected_prompt: return "Error: Unknown prompt type for Gemini analysis."
        print(f"Calling Gemini API (model: gemini-1.5-flash-latest) with prompt type: {prompt_type}")
        response = model.generate_content(selected_prompt)
        if response.prompt_feedback and response.prompt_feedback.block_reason:
            block_reason = response.prompt_feedback.block_reason
            print(f"Warning: Gemini prompt was blocked. Reason: {block_reason}")
            return f"Gemini analysis blocked: {block_reason}. Please review prompt or safety settings."
        if hasattr(response, 'text') and response.text:
            analysis_result = response.text
            print(f"Gemini analysis successful for prompt type: {prompt_type}")
            return analysis_result
        else:
            print(f"Warning: Gemini response did not contain text. Parts: {response.parts if hasattr(response, 'parts') else 'N/A'}")
            return "Gemini analysis result was empty or malformed."
    except google_exceptions.GoogleAPIError as e:
        print(f"Error during Gemini API call (GoogleAPIError): {e}")
        return f"Gemini analysis failed (GoogleAPIError): {str(e)}"
    except Exception as e:
        print(f"An unexpected error occurred during Gemini API call: {e}")
        return f"Gemini analysis failed (Unexpected Error): {str(e)}"
