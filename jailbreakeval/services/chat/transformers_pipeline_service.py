import copy
from typing import Any, Dict, Optional, Sequence, Union
from transformers.pipelines import TextGenerationPipeline
from transformers.pipelines import pipeline as pipeline_factory
from transformers import PreTrainedModel
from jailbreakeval.services.chat.service_base import ChatService


from jailbreakeval.services.chat.types import Message


class TransformersPipelineChatService(ChatService, service_type="transformers-pipeline"):
    def __init__(
        self,
        pipeline: Optional[TextGenerationPipeline] = None,
        model: Optional[Union[str, PreTrainedModel]] = None,
        chat_kwargs: Optional[Dict[str, Any]] = None,
        **pipeline_kwargs,
    ) -> None:
        self.pipeline = pipeline or pipeline_factory(task="text-generation", model=model, **pipeline_kwargs)
        super().__init__(self.pipeline.model.name_or_path, chat_kwargs)
        self.chat_kwargs["return_full_text"] = False
        self.chat_kwargs["continue_final_message"] = False

    def chat(self, conversation: Sequence[Message], **override_chat_kwargs) -> str:
        chat_kwargs = copy.deepcopy(self.chat_kwargs)
        for k in override_chat_kwargs:
            if k in chat_kwargs:
                chat_kwargs.pop(k)
        result = self.pipeline(text_inputs=conversation, **chat_kwargs, **override_chat_kwargs)
        return result[0]["generated_text"]
