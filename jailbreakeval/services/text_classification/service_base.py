from __future__ import annotations
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any, Dict, Optional


class TextClassificationService(ABC):
    @abstractmethod
    def predict(self, text: str, **override_predict_kwargs) -> Dict: ...

    def __init__(self, model: Optional[str] = None, predict_kwargs: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        super().__init__()
        self.model = model
        self.predict_kwargs = deepcopy(predict_kwargs or {})

    @classmethod
    def __init_subclass__(cls, service_type: Optional[str] = None, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if service_type:
            cls.service_type = service_type
            TextClassificationServiceFactory.register(service_type, cls)


class TextClassificationServiceFactory:
    _registered_classes: Dict[str, type[TextClassificationService]] = {}

    @classmethod
    def register(cls, service_type: str, service_class: type[TextClassificationService]) -> None:
        if not issubclass(service_class, TextClassificationService):
            raise ValueError(f"{service_class} is incompatiable with `TextClassificationService`.")
        if registered_cls := cls._registered_classes.get(service_type):
            raise ValueError(f"service type {service_type} has already be registered to {registered_cls}")
        cls._registered_classes[service_type] = service_class

    @classmethod
    def build(cls, service_type: str, **service_kwargs) -> TextClassificationService:
        if registered_cls := cls._registered_classes.get(service_type):
            return registered_cls(**service_kwargs)
        raise ValueError(f"Unkown service type {service_type}. Must be one of {cls._registered_classes.keys()}")
