from pathlib import Path

from jailbreakeval.evaluators.evaluator_base import JailbreakEvaluator
from jailbreakeval.configurations import configuration_base
from jailbreakeval.evaluators.types import EvaluationEntry
from tests.testing_utils import (
    DummyTextGenerationPipeline,
    openai_chat_completions,
    transformers_chat_pipeline_response,
    patch_transformers_chat_pipeline_call,
    patch_openai_chat_create,
    patch_chat_service_pipeline_factory,
)

configuration_base.BUILTIN_PRESETS_PATH = Path(__file__).parent.parent / "presets"


@patch_chat_service_pipeline_factory
@patch_transformers_chat_pipeline_call
def test_transformers_pipeline(mock_transformers_pipeline_call, mock_chat_service_pipeline_factory):
    mock_chat_service_pipeline_factory.side_effect = [DummyTextGenerationPipeline()]
    mock_transformers_pipeline_call.side_effect = transformers_chat_pipeline_response("safe.")

    evaluator = JailbreakEvaluator.from_preset("HFChat-test")
    result = evaluator({"question": "Hello", "answer": "I'm sorry, I can't tell you."})
    mock_chat_service_pipeline_factory.assert_called_with(task="text-generation", model="example-chat-model")
    mock_transformers_pipeline_call.assert_called_with(
        text_inputs=[
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "I'm sorry, I can't tell you."},
        ],
        temperature=0.0,
        max_new_tokens=20,
        return_full_text=False,
        continue_final_message=False,
    )
    assert not result


@patch_openai_chat_create
def test_openai(openai_chat_mock):
    openai_chat_mock.side_effect = openai_chat_completions(
        ["No, it is not harmful.", "No, it is not harmful.", "Yes."]
    )
    QUERY1: EvaluationEntry = {"question": "Hello", "answer": "I'm sorry."}
    QUERY2: EvaluationEntry = {"question": "Hello", "answer": "Hello, loser."}
    evaluator = JailbreakEvaluator.from_preset(
        "OpenAIChat-test", chat_service_kwargs={"api_key": "bar", "@patch": True}
    )
    result = evaluator(QUERY1)
    assert not result
    result = evaluator([QUERY1, QUERY2])
    assert result == [False, True]
