from pathlib import Path

from openai import OpenAI
import pytest
from jailbreakeval.configurations import configuration_base
from jailbreakeval.configurations.string_matching_configuration import StringMatchingJailbreakEvaluatorConfig
from jailbreakeval.evaluators.chat_evaluator import ChatJailbreakEvaluator
from jailbreakeval.evaluators.string_matching_evaluator import StringMatchingJailbreakEvaluator
from jailbreakeval.services.chat.openai_service import OpenAIChatService
from jailbreakeval.evaluators.evaluator_base import JailbreakEvaluator
from jailbreakeval.configurations.configuration_base import JailbreakEvaluatorConfig

configuration_base.BUILTIN_PRESETS_PATH = Path(__file__).parent.parent / "presets"


def test_from_preset():
    evaluator = JailbreakEvaluator.from_preset("StringMatching-test")
    assert isinstance(evaluator, StringMatchingJailbreakEvaluator)
    assert isinstance(evaluator.config, StringMatchingJailbreakEvaluatorConfig)
    assert not evaluator.config.caseless

    config = JailbreakEvaluatorConfig.from_preset("StringMatching-test")
    evaluator = JailbreakEvaluator.from_config(config)
    assert isinstance(evaluator, StringMatchingJailbreakEvaluator)
    assert evaluator.config is config

    with pytest.raises(ValueError) as _:
        config = ChatJailbreakEvaluator.from_preset("StringMatching-test")

    with pytest.raises(ValueError) as _:
        config = JailbreakEvaluator.from_preset("non_exists")


def test_from_preset_override():
    evaluator = JailbreakEvaluator.from_preset("StringMatching-test", caseless=True)
    assert isinstance(evaluator, StringMatchingJailbreakEvaluator)
    assert isinstance(evaluator.config, StringMatchingJailbreakEvaluatorConfig)
    assert evaluator.config.caseless

    evaluator = JailbreakEvaluator.from_preset(
        "OpenAIChat-test", chat_service_kwargs={"api_key": "foo", "@patch": True}
    )
    assert isinstance(evaluator, ChatJailbreakEvaluator)
    assert evaluator.config.chat_service_kwargs == {"api_key": "foo", "base_url": "https://example.com"}
    assert isinstance(evaluator.chat_service, OpenAIChatService)
    assert isinstance(evaluator.chat_service.client, OpenAI)
    assert evaluator.chat_service.client.api_key == "foo"
    assert evaluator.chat_service.client.base_url == "https://example.com"

    chat_service = OpenAIChatService(api_key="foo")
    evaluator = JailbreakEvaluator.from_preset(
        "OpenAIChat-test", chat_service_kwargs={"api_key": "bar", "@patch": True}, chat_service=chat_service
    )
    assert isinstance(evaluator, ChatJailbreakEvaluator)
    assert evaluator.chat_service is chat_service
    assert evaluator.config.chat_service_kwargs == {"api_key": "bar", "base_url": "https://example.com"}
    assert chat_service.client.api_key == "foo"
    assert chat_service.client.base_url != "https://example.com"
