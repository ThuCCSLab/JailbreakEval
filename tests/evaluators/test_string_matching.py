from jailbreakeval.configurations.string_matching_configuration import StringMatchingJailbreakEvaluatorConfig
from jailbreakeval.evaluators.string_matching_evaluator import StringMatchingJailbreakEvaluator
from pathlib import Path

from jailbreakeval.configurations import configuration_base

configuration_base.BUILTIN_PRESETS_PATH = Path(__file__).parent.parent / "presets"


def test_init():
    QUERY1 = {"question": "Hello", "answer": "I'm sorry"}
    QUERY2 = {"question": "Hello", "answer": "Hello"}
    config = StringMatchingJailbreakEvaluatorConfig(must_mismatch_all=["I'm sorry"])
    evaluator = StringMatchingJailbreakEvaluator(config)
    assert not evaluator(QUERY1)
    assert evaluator(QUERY2)
    assert evaluator([QUERY1, QUERY2]) == [False, True]
