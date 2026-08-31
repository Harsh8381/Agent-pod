from app.agent.ambient_scribe_agent import AmbientScribeAgent
from app.agent.context import EncounterContext


def test_ambient_scribe_parses_json_code_fence():
    context = AmbientScribeAgent._parse_response(
        '```json\n{"chief_complaint":"cough"}\n```'
    )

    assert context == EncounterContext(chief_complaint="cough")