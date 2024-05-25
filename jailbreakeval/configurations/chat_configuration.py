import copy
from typing import Any, Callable, Dict, List, Optional
from jailbreakeval.configurations.configuration_base import JailbreakEvaluatorConfig
from jailbreakeval.services.chat.types import Message


from jailbreakeval.utils import expr_to_func


class ChatJailbreakEvaluatorConfig(JailbreakEvaluatorConfig, evaluator_type="chat"):
    def __init__(
        self,
        conversation_template: List[Message],
        result_extractor_expr: Optional[str] = None,
        result_extractor: Optional[Callable[[str], Optional[bool]]] = None,
        chat_service_type: Optional[str] = None,
        chat_service_kwargs: Optional[Dict[str, Any]] = None,
        chat_model: Optional[str] = None,
        chat_kwargs: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        if not conversation_template:
            raise ValueError("must provide `conversation_template`")
        self.conversation_template = copy.deepcopy(conversation_template)
        self.chat_service_type = chat_service_type
        self.chat_service_kwargs = copy.deepcopy(chat_service_kwargs or {})
        self.chat_model = chat_model
        self.chat_kwargs = copy.deepcopy(chat_kwargs or {})
        self.result_extractor_expr = result_extractor_expr
        if result_extractor and result_extractor_expr:
            raise ValueError("can not set both `result_extractor` and `result_extractor_expr`.")
        self.result_extractor = result_extractor or expr_to_func(self.result_extractor_expr)

    def to_dict(self) -> dict[str, Any]:
        output = super().to_dict()
        output.pop("result_extractor")
        return output
