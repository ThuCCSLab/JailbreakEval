import pytest
from jailbreakeval.configurations.chat_configuration import ChatJailbreakEvaluatorConfig
from jailbreakeval.configurations.string_matching_configuration import StringMatchingJailbreakEvaluatorConfig

from jailbreakeval.configurations.configuration_base import JailbreakEvaluatorConfig
from pathlib import Path
from jailbreakeval.configurations import configuration_base

configuration_base.BUILTIN_PRESETS_PATH = Path(__file__).parent.parent / "presets"


def test_from_preset():
    # load by name
    config1 = JailbreakEvaluatorConfig.from_preset("HFChat-test")
    assert isinstance(config1, ChatJailbreakEvaluatorConfig)

    # load from yaml
    config = JailbreakEvaluatorConfig.from_preset(str(Path(__file__).parent.parent / "presets" / "HFChat-test.yaml"))
    assert isinstance(config, ChatJailbreakEvaluatorConfig)

    # load by non-exist name
    with pytest.raises(ValueError) as _:
        config = JailbreakEvaluatorConfig.from_preset("non_exist")

    # load by non-exist file
    with pytest.raises(ValueError) as _:
        config = JailbreakEvaluatorConfig.from_preset(str(Path(__file__).parent.parent / "presets" / "non-exist.yaml"))

    # wrong type
    with pytest.raises(ValueError) as _:
        config = StringMatchingJailbreakEvaluatorConfig.from_preset("HFChat-test")


def test_from_preset_override():
    # override
    config = JailbreakEvaluatorConfig.from_preset("HFChat-test")
    config.patch_attrs(
        chat_model="override",
        chat_kwargs={"temperature": 1.0, "top_p": 0.2},
        chat_service_kwargs={"foo": "bar"},
        foo="bar",
    )
    assert isinstance(config, ChatJailbreakEvaluatorConfig)
    assert not hasattr(config, "foo")
    assert config.chat_model == "override"
    assert config.chat_kwargs == {"temperature": 1.0, "top_p": 0.2}
    assert config.chat_service_kwargs == {"foo": "bar"}

    # override, patch dict
    config = JailbreakEvaluatorConfig.from_preset("HFChat-test").patch_attrs(
        chat_model="override",
        chat_kwargs={"temperature": 1.0, "top_p": 0.2, "@patch": True},
        chat_service_kwargs={"foo": "bar", "@patch": True},
        foo="bar",
    )
    assert isinstance(config, ChatJailbreakEvaluatorConfig)
    assert not hasattr(config, "foo")
    assert config.chat_model == "override"
    assert config.chat_kwargs == {"temperature": 1.0, "max_new_tokens": 20, "top_p": 0.2}
    assert config.chat_service_kwargs == {"foo": "bar"}
