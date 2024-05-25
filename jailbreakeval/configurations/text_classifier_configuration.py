import copy
from typing import Any, Callable, Dict, Optional
from jailbreakeval.configurations.configuration_base import JailbreakEvaluatorConfig


from jailbreakeval.utils import expr_to_func


class TextClassificationJailbreakEvaluatorConfig(JailbreakEvaluatorConfig, evaluator_type="text-classification"):
    def __init__(
        self,
        text_template: str,
        result_extractor_expr: Optional[str] = None,
        result_extractor: Optional[Callable[[str], Optional[bool]]] = None,
        text_classification_service_type: Optional[str] = None,
        text_classification_service_kwargs: Optional[Dict[str, Any]] = None,
        text_classification_model: Optional[str] = None,
        predict_kwargs: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        if not text_template:
            raise ValueError("must provide `text_template`")
        self.text_template = copy.deepcopy(text_template)
        self.text_classification_service_type = text_classification_service_type
        self.text_classification_service_kwargs = copy.deepcopy(text_classification_service_kwargs or {})
        self.text_classification_model = text_classification_model
        self.predict_kwargs = copy.deepcopy(predict_kwargs)
        self.result_extractor_expr = result_extractor_expr
        if result_extractor and result_extractor_expr:
            raise ValueError("can not set both `result_extractor` and `result_extractor_expr`.")
        self.result_extractor = result_extractor or expr_to_func(self.result_extractor_expr)

    def to_dict(self) -> dict[str, Any]:
        output = super().to_dict()
        output.pop("result_extractor")
        return output
