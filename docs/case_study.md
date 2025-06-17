# Case Study: Analyzing an Imaging Report

This case study demonstrates how the Imaging Report Analysis Tool can be used to process a sample medical imaging report, extract structured information, and provide AI-powered insights.

## 1. Sample Imaging Report (Chinese)

Let's assume we have the following (simplified) imaging report details:

*   **Patient Age:** 65
*   **Patient Sex:** Male
*   **Chief Complaint:** "持续性咳嗽伴有少量白痰一月余。" (Persistent cough with small amount of white sputum for over a month.)
*   **Examination Requested:** "胸部CT平扫" (Chest CT scan without contrast)
*   **Imaging Findings:**
    "双肺纹理增多、紊乱，右肺上叶可见一大小约2.5cm x 3.0cm类圆形高密度影，边缘尚清晰，呈分叶状。左肺未见明显实质性病变。双侧胸膜无增厚，胸腔无积液。"
    (Increased and disordered lung markings in both lungs. A quasi-circular high-density shadow measuring approximately 2.5cm x 3.0cm is visible in the upper lobe of the right lung, with relatively clear margins and a lobulated appearance. No obvious parenchymal lesions are seen in the left lung. Bilateral pleura are not thickened, and there is no pleural effusion.)
*   **Diagnostic Impression:**
    "右肺上叶占位性病变，考虑恶性肿瘤可能性大，建议增强CT或活检进一步明确。双肺慢性支气管炎改变。"
    (Space-occupying lesion in the upper lobe of the right lung, high possibility of malignancy; enhanced CT or biopsy recommended for further clarification. Changes consistent with chronic bronchitis in both lungs.)

## 2. Inputting the Report into the Tool

Using the web interface (as described in the [Usage Guide](./usage_guide.md)):

1.  **Navigate** to the "New Report" section.
2.  **Enter Patient Information:**
    *   Age: `65`
    *   Sex: `Male`
3.  **Enter Report Details:**
    *   Chief Complaint: `持续性咳嗽伴有少量白痰一月余。`
    *   Examination Requested: `胸部CT平扫`
    *   Imaging Findings: (Copy and paste the Chinese findings text)
    *   Diagnostic Impression: (Copy and paste the Chinese impression text)
4.  **Click "Submit Report for Analysis".**

## 3. Expected Analysis Output (Illustrative)

After the backend processes the report, the frontend would display results similar to this (actual SNOMED codes and Gemini output will vary based on live API responses and NLP term extraction):

---
**Patient & Report Information:**
*   **Age:** 65
*   **Sex:** Male
*   **Examination Requested:** 胸部CT平扫
*   **LOINC Code:** Computed tomography, chest, without contrast material (LN_CODE_EXAMPLE) - *计算机断层扫描，胸部，无造影剂*
    *(Note: The system would identify a LOINC code like 'RID34641' or similar for "CT Chest without contrast" and its Chinese translation.)*
*   **Report Timestamp:** (System generated timestamp)

---
**Reported Information:**
*   **Chief Complaint:** 持续性咳嗽伴有少量白痰一月余。
*   **Imaging Findings:** (The full Chinese text as entered)
*   **Diagnostic Impression:** (The full Chinese text as entered)

---
**Gemini LLM Analysis:**
*   **Summary:**
    "The report describes a 65-year-old male patient presenting with chronic cough. A chest CT scan revealed a 2.5cm x 3.0cm lobulated high-density lesion in the upper lobe of the right lung, highly suspicious for malignancy. Chronic bronchitis changes are also noted. Further investigation with enhanced CT or biopsy is recommended."
    *(This is an example summary; actual Gemini output will vary.)*
*   **Key Findings:**
    1.  Right upper lobe space-occupying lesion (2.5cm x 3.0cm, lobulated).
    2.  High suspicion of malignancy for the right lung lesion.
    3.  Chronic bronchitis changes in both lungs.
    4.  Recommendation for enhanced CT or biopsy.

---
**SNOMED CT Analysis (Tree):**
*(This is a simplified, illustrative example of what parts of the tree might look like. Actual codes and hierarchy will be more detailed and depend on the live SNOMED CT API and NLP extraction.)*

*   **Clinical finding** (123037004) - *临床所见*
    *   **Disorder of lung** (19569004) - *肺部疾病*
        *   **Mass of lung** (30979002) - *肺肿块*
            *   *(Relates to: Space-occupying lesion in RUL)*
        *   **Bronchitis** (64572001) - *支气管炎*
            *   **Chronic bronchitis** (18545008) - *慢性支气管炎*
    *   **Radiographic finding** (118247008) - *放射影像学发现*
        *   **Increased lung markings** (60334004) - *肺纹理增多*
        *   **High-density shadow on CT of lung** (SCT_CODE_EXAMPLE_HD_SHADOW) - *肺CT高密度影*
            *   *(Associated with: Right upper lobe lesion)*

---

## 4. How the System Achieves This (High-Level Overview)

1.  **Input & API Call:** The frontend sends the entered Chinese report text to the backend API.
2.  **LOINC Mapping:** The "Examination Requested" text ("胸部CT平扫") is processed. The system calls the LOINC API to find the corresponding standard LOINC code and its English/Chinese terms.
3.  **Text Processing & Translation (for SNOMED):**
    *   The Chinese text from "Imaging Findings" and "Diagnostic Impression" undergoes basic NLP (term identification).
    *   Identified Chinese medical terms (e.g., "右肺上叶", "高密度影", "恶性肿瘤", "慢性支气管炎") are translated to English using the Google Translate API.
4.  **SNOMED CT Lookup:**
    *   The translated English terms are then used to query the Snowstorm SNOMED CT API. This retrieves standard SNOMED CT codes and their official English preferred terms.
    *   The system also queries for parent concepts ('is-a' relationships) for each identified SNOMED CT code.
5.  **Chinese Translation of SNOMED Terms:** The official English SNOMED CT terms are translated back to Chinese using Google Translate for display.
6.  **Tree Construction:** The `build_snomed_tree` utility uses the SNOMED CT codes and their parent relationships to construct the hierarchical tree.
7.  **Gemini LLM Analysis:** The "Imaging Findings" and "Diagnostic Impression" texts are sent to the Google Gemini API with prompts to generate a summary and extract key findings.
8.  **Response to Frontend:** The backend consolidates all this structured information (LOINC, SNOMED tree, Gemini analysis, input data) into a `ReportAnalysisOutput` and sends it back to the frontend for display.

This case study illustrates the tool's capability to transform unstructured Chinese imaging report text into a more structured and analyzable format, enriched with standard terminologies and AI-driven insights.
