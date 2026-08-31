from fastapi.testclient import TestClient

from app.main import app
from app.api import routes


def test_health_check():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_retrieve_endpoint(monkeypatch):
    monkeypatch.setattr(routes, "retrieve_documents", lambda query, top_k: "context")
    client = TestClient(app)

    response = client.post("/retrieve", json={"query": "chest pain", "top_k": 3})

    assert response.status_code == 200
    assert response.json()["context"] == "context"


def test_analyze_endpoint(monkeypatch):
    class FakeService:
        def analyze(self, patient_summary):
            return {"risk_assessment": "low"}, '{"risk_assessment":"low"}'

    monkeypatch.setattr(routes, "ClinicalAnalysisService", FakeService)
    client = TestClient(app)

    response = client.post("/analyze", json={"patient_summary": "patient summary"})

    assert response.status_code == 200
    assert response.json()["risk_assessment"] == "low"


def test_empty_patient_summary_is_rejected():
    client = TestClient(app)

    response = client.post("/analyze", json={"patient_summary": ""})

    assert response.status_code == 422


def test_encounter_endpoint(monkeypatch):
    class FakeEncounterAgent:
        def process(self, transcript):
            from app.agent.context import EncounterContext

            return EncounterContext(
                transcript=transcript,
                patient_summary="Cough reported.",
                soap_note="Subjective: Cough.",
                recommendations="Monitor symptoms.",
                metadata={"agents_invoked": ["ambient_scribe", "clinical_decision_support"]},
            )

        def prepare(self, transcript):
            return self.process(transcript)

        def add_clinical_decision_support(self, context):
            return context

    monkeypatch.setattr(routes, "get_encounter_agent", lambda: FakeEncounterAgent())
    client = TestClient(app)

    response = client.post("/encounters/analyze", json={"transcript": "Patient reports cough."})

    assert response.status_code == 200
    assert response.json()["patient_summary"] == "Cough reported."
    assert response.json()["soap_note"] == "Subjective: Cough."
    assert response.json()["metadata"]["agents_invoked"] == ["ambient_scribe", "clinical_decision_support"]


def test_append_selected_insights_to_note_adds_values_under_heading():
    from frontend.streamlit_app import append_selected_insights_to_note

    summary = "Subjective: Cough.\n- **MAJOR DIAGNOSIS / ISSUES**\nAwaiting manual input."

    updated = append_selected_insights_to_note(summary, ["Hyperlipidemia", "Hypertension"])

    assert "Hyperlipidemia" in updated
    assert "Hypertension" in updated
    assert "- **MAJOR DIAGNOSIS / ISSUES**" in updated