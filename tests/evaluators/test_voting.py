from jailbreakeval.configurations.voting_configuration import VotingJailbreakEvaluatorConfig
from pathlib import Path

from jailbreakeval.configurations import configuration_base
from jailbreakeval.configurations.configuration_base import JailbreakEvaluatorConfig
from jailbreakeval.evaluators.voting_evaluator import VotingJailbreakEvaluator
from tests.testing_utils import (
    DummyTextClassificationPipeline,
    DummyTextGenerationPipeline,
    openai_chat_completions,
    transformers_chat_pipeline_response,
    patch_transformers_chat_pipeline_call,
    patch_transformers_classification_pipeline_call,
    patch_openai_chat_create,
    patch_chat_service_pipeline_factory,
    patch_text_classification_service_pipeline_factory,
)

configuration_base.BUILTIN_PRESETS_PATH = Path(__file__).parent.parent / "presets"


@patch_chat_service_pipeline_factory
@patch_transformers_chat_pipeline_call
@patch_text_classification_service_pipeline_factory
@patch_transformers_classification_pipeline_call
@patch_openai_chat_create
def test_init(
    openai_chat_mock,
    mock_transformers_classification_pipeline_call,
    mock_text_classification_service_pipeline_factory,
    mock_transformers_pipeline_call,
    mock_chat_service_pipeline_factory,
):
    openai_chat_mock.side_effect = openai_chat_completions(
        ["No, it is not harmful.", "Yes.", "No, it is not harmful.", "Yes."]
    )
    mock_chat_service_pipeline_factory.side_effect = [DummyTextGenerationPipeline()]
    mock_transformers_pipeline_call.side_effect = transformers_chat_pipeline_response(
        ["safe.", "unsafe", "safe.", "unsafe"]
    )
    mock_text_classification_service_pipeline_factory.side_effect = [DummyTextClassificationPipeline()]
    mock_transformers_classification_pipeline_call.side_effect = [
        [{"label": "LABEL_1", "score": 0.5}],
        [{"label": "LABEL_0", "score": 0.5}],
    ]
    QUERY1 = {"question": "Hello", "answer": "I'm sorry"}
    QUERY2 = {"question": "Hello", "answer": "Hello, loser."}

    config = VotingJailbreakEvaluatorConfig(
        evaluator_configs=["OpenAIChat-test", "HFChat-test", "StringMatching-test"],
        weights=[0.7, 0.8, 0.2],
        evaluator_kwargs_list=[{"chat_service_kwargs": {"api_key": "bar", "@patch": True}}, None, None],
    )
    evaluator = VotingJailbreakEvaluator(config)
    assert not evaluator(QUERY1)
    assert evaluator(QUERY2)
    config = JailbreakEvaluatorConfig.from_preset("Voting-test")
    assert isinstance(config, VotingJailbreakEvaluatorConfig)
    config.evaluator_configs[0].chat_service_kwargs["api_key"] = "aaaa"
    evaluator = VotingJailbreakEvaluator(config)
    assert not evaluator(QUERY1)
    assert evaluator(QUERY2)
