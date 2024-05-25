from typing import Optional
from jailbreakeval.services.chat.service_base import ChatService, ChatServiceFactory
from jailbreakeval.configurations.chat_configuration import ChatJailbreakEvaluatorConfig
from jailbreakeval.configurations.configuration_base import JailbreakEvaluatorConfig
from jailbreakeval.evaluators.evaluator_base import IteratedJailbreakEvaluator
from jailbreakeval.evaluators.types import EvaluationEntry
from jinja2 import Template

from jailbreakeval.services.chat.types import Message


class ChatJailbreakEvaluator(
    IteratedJailbreakEvaluator, evaluator_type="chat", config_class=ChatJailbreakEvaluatorConfig
):
    def __init__(self, config: JailbreakEvaluatorConfig, chat_service: Optional[ChatService] = None, **kwargs) -> None:
        super().__init__(config, **kwargs)
        self.chat_service = chat_service or ChatServiceFactory.build(
            service_type=self.config.chat_service_type,
            model=self.config.chat_model,
            chat_kwargs=self.config.chat_kwargs,
            **self.config.chat_service_kwargs,
        )

    def _format_conversation(self, conversation_template, entry) -> list[Message]:
        return [
            {
                "role": message["role"],
                "content": Template(message["content"]).render(**entry),
            }
            for message in conversation_template
        ]

    def _eval_single(self, entry: EvaluationEntry, **kwargs) -> Optional[bool]:
        messages = self._format_conversation(self.config.conversation_template, entry)
        response = self.chat_service.chat(messages)
        return self.config.result_extractor(response)
