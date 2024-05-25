from typing import Any, Callable, Dict, Union, Literal, List, Optional
from jailbreakeval.configurations.configuration_base import JailbreakEvaluatorConfig


class StringMatchingJailbreakEvaluatorConfig(JailbreakEvaluatorConfig, evaluator_type="string-matching"):
    _MATCHING_POSITION_TO_PREDICATE_: Dict[str, Callable[[str, str], bool]] = {
        "prefix": str.startswith,
        "suffix": str.endswith,
        "substring": str.__contains__,
        "whole": str.__eq__,
    }

    def __init__(
        self,
        matching: Union[Literal["prefix"], Literal["suffix"], Literal["substring"], Literal["whole"]] = "prefix",
        predicate: Optional[Callable[[str, str], bool]] = None,
        caseless: bool = False,
        must_match_any: Optional[List[str]] = None,
        must_match_all: Optional[List[str]] = None,
        must_mismatch_all: Optional[List[str]] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.predicate = predicate or self._MATCHING_POSITION_TO_PREDICATE_.get(matching)
        if not self.predicate:
            raise ValueError("Expect a valid `matching` field.")

        self.matching = matching

        self.caseless = caseless

        lists = (must_match_any, must_match_all, must_mismatch_all)
        if not any(lists):
            raise ValueError("Must provide one matching object.")

        self.must_match_any, self.must_match_all, self.must_mismatch_all = (
            ([] if targets is None else ([x.casefold() for x in targets] if self.caseless else list(targets)))
            for targets in lists
        )

    def to_dict(self) -> Dict[str, Any]:
        output = super().to_dict()
        output.pop("predicate")
        return output
