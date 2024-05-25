from __future__ import annotations
from abc import ABC, abstractmethod
import os
from typing import Any, List, Optional, Sequence, Union, overload

from tqdm import tqdm

from jailbreakeval.configurations.configuration_base import JailbreakEvaluatorConfig
from jailbreakeval.evaluators.types import EvaluationEntry
import logging

logger = logging.getLogger(__name__)


class JailbreakEvaluator(ABC):
    _registered_: dict[str, type[JailbreakEvaluator]] = {}
    config_class: type[JailbreakEvaluatorConfig]

    def __init__(self, config: JailbreakEvaluatorConfig, **kwargs) -> None:
        super().__init__()
        if not isinstance(config, JailbreakEvaluatorConfig):
            raise TypeError("Expect `config` to be `JailbreakEvaluatorConfig`")
        self.config = config

    def __init_subclass__(
        cls,
        evaluator_type: Optional[str] = None,
        config_class: Optional[type[JailbreakEvaluatorConfig]] = None,
        **kwargs,
    ) -> None:
        super().__init_subclass__(**kwargs)
        if evaluator_type is not None:
            if type_ := cls._registered_.get(evaluator_type):
                raise ValueError(f"JailbreakEvaluator with id {evaluator_type} has already been registered as {type_}")
            cls._registered_[evaluator_type] = cls
        if config_class:
            cls.config_class = config_class

    @classmethod
    def from_preset(cls, name_or_yaml_file: Union[str, os.PathLike], **kwargs):
        """
        Create an instance of the evaluator class using a preset configuration.

        Args:
            name_or_yaml_file (Union[str, os.PathLike]): The name of the preset or path to a YAML file.
            **kwargs: Additional keyword arguments to override evaluator config. Extra arguments will be provided to the evaluator's contrustructor.

        Returns:
            An instance of the class initialized with the preset configuration.
        """

        config = JailbreakEvaluatorConfig.from_preset(name_or_yaml_file)

        return cls.from_config(config, **kwargs)

    @classmethod
    def from_config(cls, config: JailbreakEvaluatorConfig, **kwargs):
        """
        Creates an instance of the evaluator class based on the provided configuration.

        Args:
            config (JailbreakEvaluatorConfig): The configuration object for the evaluator.
            **kwargs: Additional keyword arguments provided to the evaluator's contrustructor.

        Returns:
            JailbreakEvaluator: An instance of the evaluator class based on the provided configuration.

        Raises:
            ValueError: If the evaluator_type in the config is not recognized, incompatible, or if the config is incompatible with the evaluator class.
        """

        config.patch_attrs(**kwargs)

        evaluator_type = config.evaluator_type
        if evaluator_type not in cls._registered_:
            raise ValueError(
                f"unrecognized `evaluator_type` {evaluator_type}. Must be one of the following: {cls._registered_.keys()}"
            )
        evaluator_class = cls._registered_[evaluator_type]
        if not issubclass(evaluator_class, cls):
            raise ValueError(f"`evaluator_type` {evaluator_type} is incompatible with {evaluator_class}")
        if not isinstance(config, evaluator_class.config_class):
            raise ValueError(f"`evaluator_type` {evaluator_type} is incompatible with {evaluator_class}")

        return evaluator_class(config, **kwargs)

    @property
    def name_or_path(self):
        return self.config.name_or_path

    @abstractmethod
    @overload
    def __call__(self, data: Sequence[EvaluationEntry], **kwargs) -> List[Union[bool, None]]: ...

    @abstractmethod
    @overload
    def __call__(self, data: EvaluationEntry, **kwargs) -> Union[bool, None]: ...

    @abstractmethod
    def __call__(self, data, **kwargs) -> Any: ...


class IteratedJailbreakEvaluator(JailbreakEvaluator):
    def __call__(self, data, **kwargs) -> Any:
        disable_tqdm = kwargs.pop("disable_tqdm", False)

        is_batched_input = not isinstance(data, dict)

        return (
            [self._eval_single(entry) for entry in (data if disable_tqdm else tqdm(data))]
            if is_batched_input
            else self._eval_single(data)
        )

    @abstractmethod
    def _eval_single(self, entry: EvaluationEntry, **kwargs) -> Union[bool, None]: ...
