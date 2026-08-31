import pytest

from app.services.clinical_service import parse_model_response


def test_parse_model_response_accepts_json_code_fence():
    assert parse_model_response('```json\n{"risk_assessment": "low"}\n```') == {
        "risk_assessment": "low"
    }


def test_parse_model_response_rejects_non_object_json():
    with pytest.raises(ValueError, match="JSON object"):
        parse_model_response("[]")