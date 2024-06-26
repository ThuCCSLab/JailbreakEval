from typing import Optional

from jailbreakeval.evaluators.evaluator_base import IteratedJailbreakEvaluator
from jailbreakeval.evaluators.types import EvaluationEntry
from jinja2 import Template

from jailbreakeval.services.text_classification.service_base import (
    TextClassificationService,
    TextClassificationServiceFactory,
)
from jailbreakeval.configurations.text_classifier_configuration import TextClassificationJailbreakEvaluatorConfig


class TextClassificationJailbreakEvaluator(
    IteratedJailbreakEvaluator,
    evaluator_type="text-classification",
    config_class=TextClassificationJailbreakEvaluatorConfig,
):
    def __init__(
        self,
        config: TextClassificationJailbreakEvaluatorConfig,
        text_classification_service: Optional[TextClassificationService] = None,
        **kwargs,
    ) -> None:
        super().__init__(config, **kwargs)
        self.text_classification_service = text_classification_service or TextClassificationServiceFactory.build(
            service_type=self.config.text_classification_service_type,
            model=self.config.text_classification_model,
            predict_kwargs=self.config.predict_kwargs,
            **self.config.text_classification_service_kwargs,
        )

    def _format_text(self, text_template, entry):
        return Template(text_template).render(**entry)

    def _eval_single(self, entry: EvaluationEntry, **kwargs) -> Optional[bool]:
        messages = self._format_text(self.config.text_template, entry)
        response = self.text_classification_service.predict(messages)
        return self.config.result_extractor(response)
