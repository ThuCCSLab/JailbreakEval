from jailbreakeval.services.text_classification.service_base import TextClassificationService
import copy
from typing import Any, Dict, Optional, Union
from transformers.pipelines import TextClassificationPipeline
from transformers.pipelines import pipeline as pipeline_factory
from transformers import PreTrainedModel


class TransformersPipelineTextClassificationService(TextClassificationService, service_type="transformers-pipeline"):
    def __init__(
        self,
        pipeline: Optional[TextClassificationPipeline] = None,
        model: Optional[Union[str, PreTrainedModel]] = None,
        predict_kwargs: Optional[Dict[str, Any]] = None,
        **pipeline_kwargs,
    ) -> None:
        self.pipeline = pipeline or pipeline_factory(task="text-classification", model=model, **pipeline_kwargs)
        super().__init__(self.pipeline.model.name_or_path, predict_kwargs)

    def predict(self, text: str, **override_predict_kwargs) -> Dict:
        predict_kwargs = copy.deepcopy(self.predict_kwargs)
        for k in override_predict_kwargs:
            if k in predict_kwargs:
                predict_kwargs.pop(k)
        if not isinstance(text, str):
            raise NotImplementedError("Do not support batch predict.")

        # make sure input length within context length
        input_len = len(self.pipeline.tokenizer(text).input_ids)
        tokenizer_max_length = self.pipeline.tokenizer.model_max_length

        model_max_length = self.pipeline.model.config.max_position_embeddings

        if input_len > tokenizer_max_length:
            return {
                "error": f"input length is longer than tokenizer's max length ({input_len} > {tokenizer_max_length})."
            }

        if input_len > model_max_length:
            return {"error": f"input length is longer than model's max length ({input_len} > {tokenizer_max_length})."}

        result = self.pipeline(inputs=text, **predict_kwargs, **override_predict_kwargs)
        return result[0]
