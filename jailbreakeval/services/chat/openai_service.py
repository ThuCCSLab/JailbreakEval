import copy
import logging
from typing import Any, Dict, Optional, Sequence
from openai import OpenAI

from jailbreakeval.services.chat.service_base import ChatService
from jailbreakeval.services.chat.types import Message


logger = logging.getLogger(__name__)


class OpenAIChatService(ChatService, service_type="openai"):
    def __init__(
        self,
        client: Optional[OpenAI] = None,
        model: Optional[str] = None,
        chat_kwargs: Optional[Dict[str, Any]] = None,
        **client_kwargs,
    ) -> None:
        super().__init__(model, chat_kwargs)

        self.client = client or OpenAI(**client_kwargs)

        self.prompt_tokens_usage = 0
        self.completion_tokens_usage = 0

    def chat(self, conversation: Sequence[Message], **override_chat_kwargs):
        chat_kwargs = copy.deepcopy(self.chat_kwargs)
        for k in override_chat_kwargs:
            if k in chat_kwargs:
                chat_kwargs.pop(k)
        response = self.client.chat.completions.create(
            messages=conversation, model=self.model, **chat_kwargs, **override_chat_kwargs
        )
        logger.debug(
            f"OpenAIChat response id:{response.id}, prompt_tokens_usage: {response.usage.prompt_tokens}, completion_tokens_usage: {response.usage.completion_tokens}, prompt: {conversation}, completion: {response.choices[0].message.content}"
        )
        self.prompt_tokens_usage += response.usage.prompt_tokens
        self.completion_tokens_usage += response.usage.completion_tokens
        return response.choices[0].message.content
