from app.agent.ambient_scribe_agent import AmbientScribeAgent
from app.agent.context import EncounterContext


def test_ambient_scribe_parses_json_code_fence():
    context = AmbientScribeAgent._parse_response(
        '```json\n{"chief_complaint":"cough"}\n```'
    )

    assert context == EncounterContext(chief_complaint="cough")


def test_soap_note_falls_back_to_patient_summary_when_fields_are_empty():
    context = EncounterContext(
        patient_summary="Chief Complaint:\nFever\n\nHistory of Present Illness:\nPatient has fever.\n\nAssessment:\nPossible infection.\n\nPlan:\nOrder labs.",
    )

    note = context.as_soap_note()

    assert "Subjective:" in note
    assert "Fever" in note
    assert "Assessment:" in note
    assert "Order labs." in note