import copy
from typing import Any, Dict, Optional

from openai import OpenAI
from jailbreakeval.services.text_classification.service_base import TextClassificationService


class OpenAITextClassificationService(TextClassificationService, service_type="openai"):
    def __init__(
        self,
        client: Optional[OpenAI] = None,
        model: Optional[str] = None,
        predict_kwargs: Optional[Dict[str, Any]] = None,
        **client_kwargs,
    ) -> None:
        super().__init__(model, predict_kwargs)

        self.client = client or OpenAI(**client_kwargs)

    def predict(self, text: str, **override_predict_kwargs) -> Dict:
        predict_kwargs = copy.deepcopy(self.predict_kwargs)
        for k in override_predict_kwargs:
            if k in predict_kwargs:
                predict_kwargs.pop(k)
        if not isinstance(text, str):
            raise NotImplementedError("Do not support batch predict.")
        result = self.client.moderations.create(
            input=text, model=self.model, **predict_kwargs, **override_predict_kwargs
        )
        return result.results[0].model_dump()
