from pathlib import Path
from unittest.mock import patch
from jailbreakeval.services.text_classification.perspective_service import PerspectiveTextClassificationService
from googleapiclient import discovery


@patch("googleapiclient.discovery.build")
@patch("googleapiclient.http.HttpRequest.execute")
def test_init(mock_discovery_http_execute, mock_discovery_build):
    discovery_document = (Path(__file__).parent.parent.parent / "data" / "perspective_document.json").read_text()
    mock_discovery_build.side_effect = [discovery.build_from_document(developerKey="123", service=discovery_document)]
    RESULT = {
        "attributeScores": {
            "TOXICITY": {
                "spanScores": [{"begin": 0, "end": 13, "score": {"value": 0.96426713, "type": "PROBABILITY"}}],
                "summaryScore": {"value": 0.96426713, "type": "PROBABILITY"},
            },
            "SEVERE_TOXICITY": {
                "spanScores": [{"begin": 0, "end": 13, "score": {"value": 0.5454843, "type": "PROBABILITY"}}],
                "summaryScore": {"value": 0.5454843, "type": "PROBABILITY"},
            },
        },
        "languages": ["en"],
        "detectedLanguages": ["en"],
    }
    mock_discovery_http_execute.side_effect = [RESULT]

    service = PerspectiveTextClassificationService(
        base_url="https://perspective-proxy.example.com/", api_key="aaa", attributes=["SEVERE_TOXICITY", "TOXICITY"]
    )

    result = service.predict("Hello, World!")
    assert isinstance(result, dict)
    assert result is RESULT
