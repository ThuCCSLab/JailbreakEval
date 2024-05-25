import os
from jailbreakeval.services.text_classification.transformers_pipeline_service import (
    TransformersPipelineTextClassificationService,
)
from transformers.pipelines import TextClassificationPipeline
from transformers.pipelines import pipeline as pipeline_factory
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from tests.testing_utils import DummyTextClassificationPipeline, patch_transformers_classification_pipeline_call

MODEL = os.environ.get("TEST_CLASSIFICATION_MODEL", "Elron/bleurt-tiny-512")


def test_init():
    service = TransformersPipelineTextClassificationService(model=MODEL)
    assert service.model == MODEL
    assert isinstance(service.pipeline, TextClassificationPipeline)

    model = AutoModelForSequenceClassification.from_pretrained(MODEL)
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    service = TransformersPipelineTextClassificationService(model=model, tokenizer=tokenizer)
    assert service.model == MODEL
    assert isinstance(service.pipeline, TextClassificationPipeline)
    assert service.pipeline.model is model
    assert service.pipeline.tokenizer is tokenizer

    pipeline = pipeline_factory("text-classification", model=model, tokenizer=tokenizer)
    service = TransformersPipelineTextClassificationService(pipeline=pipeline)
    assert service.model == MODEL
    assert service.pipeline is pipeline
    assert service.pipeline.model is model
    assert service.pipeline.tokenizer is tokenizer


@patch_transformers_classification_pipeline_call
def test_predict(mock_transformers_classification_pipeline_call):
    TEXT = "I love you!"
    RESPONSE = {"label": "LABEL_0", "score": 0.5}

    mock_transformers_classification_pipeline_call.side_effect = [[RESPONSE]] * 4

    service = TransformersPipelineTextClassificationService(pipeline=DummyTextClassificationPipeline())
    result = service.predict(TEXT)
    mock_transformers_classification_pipeline_call.assert_called_with(inputs=TEXT)
    assert isinstance(result, dict)
    assert result == RESPONSE

    result = service.predict(TEXT, key="value")
    mock_transformers_classification_pipeline_call.assert_called_with(inputs=TEXT, key="value")
    assert isinstance(result, dict)
    assert result == RESPONSE

    service = TransformersPipelineTextClassificationService(
        model=MODEL, predict_kwargs={"hello": "world", "foo": "bar"}
    )
    result = service.predict(TEXT)
    mock_transformers_classification_pipeline_call.assert_called_with(inputs=TEXT, hello="world", foo="bar")
    assert isinstance(result, dict)
    assert result == RESPONSE

    result = service.predict(TEXT, foo="baz", key="value")
    mock_transformers_classification_pipeline_call.assert_called_with(
        inputs=TEXT, hello="world", foo="baz", key="value"
    )
    assert isinstance(result, dict)
    assert result == RESPONSE
