from __future__ import annotations
import copy
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union
import yaml

BUILTIN_PRESETS_PATH = Path(__file__).parent.parent / "presets"


class JailbreakEvaluatorConfig:
    _registered_: dict[str, type[JailbreakEvaluatorConfig]] = {}

    evaluator_type: str = ""

    attribute_map: Dict[str, str] = {}

    def __setattr__(self, key, value):
        if key in super().__getattribute__("attribute_map"):
            key = super().__getattribute__("attribute_map")[key]
        super().__setattr__(key, value)

    def __getattribute__(self, key):
        if key != "attribute_map" and key in super().__getattribute__("attribute_map"):
            key = super().__getattribute__("attribute_map")[key]
        return super().__getattribute__(key)

    def __init_subclass__(cls, evaluator_type: Optional[str] = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if evaluator_type:
            cls.evaluator_type = evaluator_type
            cls._registered_[evaluator_type] = cls

    def __init__(self, **kwargs) -> None:
        self.name_or_path = str(kwargs.pop("name_or_path", ""))

    @classmethod
    def from_preset(cls, name_or_yaml_file: Union[str, os.PathLike]) -> JailbreakEvaluatorConfig:
        """
        Creates an JailbreakEvaluatorConfig object from a preset defined in a YAML file.

        Args:
            name_or_yaml_file (Union[str, os.PathLike]): The name of the preset or path of the YAML file containing the preset configuration.

        Returns:
            JailbreakEvaluatorConfig: An instance of JailbreakEvaluatorConfig based on the preset configuration.

        Raises:
            ValueError: If the YAML file is not found, the preset is unrecognized, or the evaluator type is incompatible.

        Examples:
            config = JailbreakEvaluatorConfig.from_preset("my_preset.yaml")
        """

        yaml_file_path = Path(name_or_yaml_file).resolve()

        if not yaml_file_path.is_file():
            yaml_file_path = (BUILTIN_PRESETS_PATH / name_or_yaml_file).with_suffix(".yaml")
            if not yaml_file_path.is_file():
                raise ValueError(f"Unreconized evaluator preset {name_or_yaml_file}.")

        config_dict = yaml.safe_load(yaml_file_path.read_text(encoding="utf-8"))

        config_dict["name_or_path"] = name_or_yaml_file

        return cls.from_dict(config_dict)

    def patch_attrs(self, **kwargs) -> JailbreakEvaluatorConfig:
        to_remove = []
        for key, value in kwargs.items():
            if hasattr(self, key):
                if isinstance(getattr(self, key), dict) and isinstance(value, dict) and value.get("@patch", False):
                    for k, v in value.items():
                        if k != "@patch":
                            getattr(self, key)[k] = v
                else:
                    setattr(self, key, value)
                to_remove.append(key)
        for key in to_remove:
            kwargs.pop(key)
        return self

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> JailbreakEvaluatorConfig:
        name_or_yaml_file = data.get("name_or_path", "")

        evaluator_type = data.get("evaluator_type")

        if evaluator_type not in cls._registered_:
            raise ValueError(
                f"Preset {name_or_yaml_file} has unrecognized `evaluator_type` {evaluator_type}. Must be one of the following: {cls._registered_.keys()}"
            )

        config_class = cls._registered_[evaluator_type]
        if not issubclass(config_class, cls):
            raise ValueError(
                f"Preset {name_or_yaml_file} has `evaluator_type` {evaluator_type} that is incompatible with {config_class}"
            )

        return config_class(**data)

    def to_dict(self) -> dict[str, Any]:
        output = copy.deepcopy(self.__dict__)
        output["evaluator_type"] = self.__class__.evaluator_type
        for key, value in output.items():
            # Deal with nested configs like CLIP
            if isinstance(value, JailbreakEvaluatorConfig):
                value = value.to_dict()
            output[key] = value
        return output

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {json.dumps(self.to_dict(), indent=2, sort_keys=True)}"

    def __str__(self) -> str:
        return repr(self)
