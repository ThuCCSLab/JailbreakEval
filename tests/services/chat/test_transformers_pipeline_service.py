from jailbreakeval.services.chat.transformers_pipeline_service import TransformersPipelineChatService

from transformers.pipelines import TextGenerationPipeline
from transformers.pipelines import pipeline as pipeline_factory
from transformers import AutoModelForCausalLM, AutoTokenizer
from tests.testing_utils import patch_transformers_chat_pipeline_call, transformers_chat_pipeline_response
import os

MODEL = os.environ.get("TEST_CHAT_MODEL", "trl-internal-testing/tiny-random-LlamaForCausalLM")


def test_init():
    # by model name
    service = TransformersPipelineChatService(model=MODEL)
    assert service.model == MODEL
    assert isinstance(service.pipeline, TextGenerationPipeline)

    # by existing model
    model = AutoModelForCausalLM.from_pretrained(MODEL)
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    service = TransformersPipelineChatService(model=model, tokenizer=tokenizer)
    assert service.model == MODEL
    assert isinstance(service.pipeline, TextGenerationPipeline)
    assert service.pipeline.model is model
    assert service.pipeline.tokenizer is tokenizer

    # by existing pipeline
    pipeline = pipeline_factory("text-generation", model=model, tokenizer=tokenizer)
    service = TransformersPipelineChatService(pipeline=pipeline)
    assert service.model == MODEL
    assert service.pipeline is pipeline
    assert service.pipeline.model is model
    assert service.pipeline.tokenizer is tokenizer


@patch_transformers_chat_pipeline_call
def test_predict(mock_transformers_pipeline_call):
    MESSAGES = [{"role": "user", "content": "Hello."}]
    RESPONSE = "This is a mock response, how can I help you?"

    mock_transformers_pipeline_call.side_effect = transformers_chat_pipeline_response([RESPONSE] * 4)

    service = TransformersPipelineChatService(model=MODEL)
    response = service.chat(MESSAGES)
    mock_transformers_pipeline_call.assert_called_with(
        text_inputs=MESSAGES, return_full_text=False, continue_final_message=False
    )
    assert isinstance(response, str)
    assert response == RESPONSE

    # override
    response = service.chat(MESSAGES, key="value")
    mock_transformers_pipeline_call.assert_called_with(
        text_inputs=MESSAGES, key="value", return_full_text=False, continue_final_message=False
    )
    assert isinstance(response, str)
    assert response == RESPONSE

    # gen_kwargs
    service = TransformersPipelineChatService(model=MODEL, chat_kwargs={"hello": "world", "foo": "bar"})
    response = service.chat(MESSAGES)

    mock_transformers_pipeline_call.assert_called_with(
        text_inputs=MESSAGES, hello="world", foo="bar", return_full_text=False, continue_final_message=False
    )
    assert isinstance(response, str)
    assert response == RESPONSE

    # gen_kwargs + override
    response = service.chat(MESSAGES, foo="baz", key="value", return_full_text=False, continue_final_message=False)

    mock_transformers_pipeline_call.assert_called_with(
        text_inputs=MESSAGES,
        hello="world",
        foo="baz",
        key="value",
        return_full_text=False,
        continue_final_message=False,
    )
    assert isinstance(response, str)
    assert response == RESPONSE
