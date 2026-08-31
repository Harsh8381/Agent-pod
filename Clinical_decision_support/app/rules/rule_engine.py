import re
from typing import Dict, List, Optional


def _extract_hba1c(patient_summary: str) -> Optional[float]:
    """Extract HbA1c value from a patient summary."""
    patterns = [
        r"hba1c\s*(?:is|=|:)?\s*(\d+(?:\.\d+)?)\s*%?",
        r"a1c\s*(?:is|=|:)?\s*(\d+(?:\.\d+)?)\s*%?",
    ]
    for pattern in patterns:
        match = re.search(pattern, patient_summary, flags=re.IGNORECASE)
        if match:
            return float(match.group(1))
    return None


def _extract_bp(patient_summary: str) -> Optional[Dict[str, int]]:
    """Extract blood pressure from a patient summary."""
    patterns = [
        r"\bbp\s*(?:is|=|:)?\s*(\d{2,3})\s*/\s*(\d{2,3})",
        r"blood pressure\s*(?:is|=|:)?\s*(\d{2,3})\s*/\s*(\d{2,3})",
    ]
    for pattern in patterns:
        match = re.search(pattern, patient_summary, flags=re.IGNORECASE)
        if match:
            return {"systolic": int(match.group(1)), "diastolic": int(match.group(2))}
    return None


def detect_clinical_risks(patient_summary: str) -> List[Dict[str, str]]:
    """Detect structured clinical risks and care gaps from a patient summary."""
    alerts = []
    if not patient_summary or not patient_summary.strip():
        return alerts

    summary_lower = patient_summary.lower()

    hba1c = _extract_hba1c(patient_summary)
    if hba1c is not None and hba1c > 9:
        alerts.append(
            {
                "title": "Uncontrolled Diabetes",
                "severity": "high",
                "trigger": f"HbA1c value is {hba1c}%, which is greater than 9%.",
                "rule_id": "RULE_DM_HBA1C_GT_9",
                "category": "diabetes",
            }
        )

    bp = _extract_bp(patient_summary)
    if bp is not None:
        systolic = bp["systolic"]
        diastolic = bp["diastolic"]
        if systolic > 140 or diastolic > 90:
            alerts.append(
                {
                    "title": "Elevated Blood Pressure",
                    "severity": "high",
                    "trigger": f"Blood pressure is {systolic}/{diastolic}, which is above 140/90.",
                    "rule_id": "RULE_HTN_BP_GT_140_90",
                    "category": "hypertension",
                }
            )

    chest_pain_terms = ["chest pain", "chest discomfort", "pressure in chest", "tightness in chest"]
    if any(term in summary_lower for term in chest_pain_terms):
        alerts.append(
            {
                "title": "Possible Acute Chest Pain Concern",
                "severity": "critical",
                "trigger": "Patient summary mentions chest pain or chest discomfort.",
                "rule_id": "RULE_CARDIAC_CHEST_PAIN",
                "category": "cardiology",
            }
        )

    retinal_gap_patterns = [
        "no retinal exam",
        "no eye exam",
        "retinal exam in 2 years",
        "eye exam in 2 years",
        "missed retinal exam",
        "overdue retinal exam",
        "last retinal exam 2 years ago",
        "not had a retinal exam",
    ]
    if any(pattern in summary_lower for pattern in retinal_gap_patterns):
        alerts.append(
            {
                "title": "Retinal Screening Gap",
                "severity": "medium",
                "trigger": "Patient appears overdue for retinal or eye examination.",
                "rule_id": "RULE_DM_RETINAL_EXAM_GAP",
                "category": "preventive_care",
            }
        )

    allergy_patterns = ["allergy", "allergic to", "drug allergy", "medication allergy", "penicillin allergy", "sulfa allergy"]
    if any(pattern in summary_lower for pattern in allergy_patterns):
        alerts.append(
            {
                "title": "Medication Allergy Safety Alert",
                "severity": "high",
                "trigger": "Patient summary mentions medication allergy or allergy history.",
                "rule_id": "RULE_MED_ALLERGY",
                "category": "medication_safety",
            }
        )

    return alerts


def run_rule_engine(patient_summary: str) -> List[Dict[str, str]]:
    return detect_clinical_risks(patient_summary)
