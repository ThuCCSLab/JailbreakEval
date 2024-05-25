from pathlib import Path
from googleapiclient import discovery
from unittest.mock import patch
from jailbreakeval.evaluators.evaluator_base import JailbreakEvaluator
from jailbreakeval.configurations import configuration_base
from jailbreakeval.configurations.configuration_base import JailbreakEvaluatorConfig
from tests.testing_utils import (
    DummyTextClassificationPipeline,
    patch_openai_moderation_create,
    openai_moderations,
    patch_transformers_classification_pipeline_call,
    patch_text_classification_service_pipeline_factory,
)

configuration_base.BUILTIN_PRESETS_PATH = Path(__file__).parent.parent / "presets"


@patch_text_classification_service_pipeline_factory
@patch_transformers_classification_pipeline_call
def test_transformers_pipeline(
    mock_transformers_classification_pipeline_call, mock_text_classification_service_pipeline_factory
):
    mock_text_classification_service_pipeline_factory.side_effect = [DummyTextClassificationPipeline()]
    mock_transformers_classification_pipeline_call.side_effect = [
        [{"label": "LABEL_1", "score": 0.5}],
        [{"label": "LABEL_0", "score": 0.5}],
    ]
    evaluator = JailbreakEvaluator.from_preset("HFTextClassification-test")
    mock_text_classification_service_pipeline_factory.assert_called_with(
        task="text-classification", model="example-classification-model"
    )

    result = evaluator({"question": "Hello", "answer": "Kill yourself."})
    assert result

    result = evaluator({"question": "Hello", "answer": "I'm sorry"})
    assert isinstance(result, bool)
    assert not result


@patch_openai_moderation_create
def test_openai(mock_openai_moderation_create):
    mock_openai_moderation_create.side_effect = openai_moderations([False, True])
    config = JailbreakEvaluatorConfig.from_preset("OpenAITextClassification-test")
    config.text_classification_service_kwargs["api_key"] = "foo"
    evaluator = JailbreakEvaluator.from_config(config)
    result = evaluator({"question": "Hello", "answer": "I'm sorry"})
    assert not result
    result = evaluator({"question": "Hello", "answer": "Go to kill yourself."})
    assert result


@patch("googleapiclient.discovery.build")
@patch("googleapiclient.http.HttpRequest.execute")
def test_perspective(mock_discovery_http_execute, mock_discovery_build):
    discovery_document = (Path(__file__).parent.parent / "data" / "perspective_document.json").read_text()
    mock_discovery_build.side_effect = [discovery.build_from_document(developerKey="123", service=discovery_document)]
    RESULT1 = {
        "attributeScores": {
            "TOXICITY": {
                "summaryScore": {"value": 0.96426713, "type": "PROBABILITY"},
            },
            "SEVERE_TOXICITY": {
                "summaryScore": {"value": 0.5454843, "type": "PROBABILITY"},
            },
        },
        "languages": ["en"],
        "detectedLanguages": ["en"],
    }
    RESULT2 = {
        "attributeScores": {
            "TOXICITY": {
                "summaryScore": {"value": 0.2, "type": "PROBABILITY"},
            },
            "SEVERE_TOXICITY": {
                "summaryScore": {"value": 0.5454843, "type": "PROBABILITY"},
            },
        },
        "languages": ["en"],
        "detectedLanguages": ["en"],
    }
    mock_discovery_http_execute.side_effect = [RESULT1, RESULT2]

    config = JailbreakEvaluatorConfig.from_preset("PerspectiveTextClassification-test")
    config.text_classification_service_kwargs["api_key"] = "foo"
    evaluator = JailbreakEvaluator.from_config(config)
    result = evaluator({"question": "Hello", "answer": "Go to kill yourself."})
    assert result
    result = evaluator({"question": "Hello", "answer": "Hello."})
    assert not result
