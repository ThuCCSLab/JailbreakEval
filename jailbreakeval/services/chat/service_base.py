from __future__ import annotations
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any, Dict, Optional, Sequence

from jailbreakeval.services.chat.types import Message


class ChatService(ABC):
    @abstractmethod
    def chat(self, conversation: Sequence[Message], **override_chat_kwargs) -> str: ...

    def __init__(self, model: Optional[str] = None, chat_kwargs: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        super().__init__()
        self.model = model
        self.chat_kwargs = deepcopy(chat_kwargs or {})

    @classmethod
    def __init_subclass__(cls, service_type: Optional[str] = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if service_type:
            cls.service_type = service_type
            ChatServiceFactory.register(service_type, cls)


class ChatServiceFactory:
    _registered_classes: Dict[str, type[ChatService]] = {}

    @classmethod
    def register(cls, service_type: str, service_class: type[ChatService]) -> None:
        if not issubclass(service_class, ChatService):
            raise ValueError(f"{service_class} is incompatiable with `ChatService`.")
        if registered_cls := cls._registered_classes.get(service_type):
            raise ValueError(f"service type {service_type} has already be registered to {registered_cls}")
        cls._registered_classes[service_type] = service_class

    @classmethod
    def build(cls, service_type: str, **service_kwargs) -> ChatService:
        if registered_cls := cls._registered_classes.get(service_type):
            return registered_cls(**service_kwargs)
        raise ValueError(f"Unkown service type {service_type}. Must be one of {cls._registered_classes.keys()}")
