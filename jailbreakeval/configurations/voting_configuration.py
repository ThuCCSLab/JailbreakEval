import os
from typing import Any, Dict, Union, List, Optional
from jailbreakeval.configurations.configuration_base import JailbreakEvaluatorConfig


class VotingJailbreakEvaluatorConfig(JailbreakEvaluatorConfig, evaluator_type="voting"):
    def __init__(
        self,
        evaluator_configs: List[Union[str, os.PathLike, JailbreakEvaluatorConfig, Dict[str, Any]]],
        evaluator_kwargs_list: Optional[List[Union[Dict[str, Any], None]]] = None,
        weights: Optional[List[float]] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        evaluator_count = len(evaluator_configs)
        if evaluator_kwargs_list:
            assert len(evaluator_kwargs_list) == evaluator_count
            self.evaluator_kwargs_list = [evaluator_kwargs or {} for evaluator_kwargs in evaluator_kwargs_list]
        else:
            self.evaluator_kwargs_list = [{} for _ in range(evaluator_count)]

        self.weights = weights or [1.0] * evaluator_count
        assert len(self.weights) == evaluator_count

        self.evaluator_configs = [
            JailbreakEvaluatorConfig.from_preset(evaluator_config)
            if isinstance(evaluator_config, (str, os.PathLike))
            else JailbreakEvaluatorConfig.from_dict(
                evaluator_config | {"name_or_path": f"{self.name_or_path}_subevaluator_{i}"}
            )
            if isinstance(evaluator_config, dict)
            else evaluator_config
            for i, evaluator_config in enumerate(evaluator_configs)
        ]

    def to_dict(self) -> Dict[str, Any]:
        output = super().to_dict()
        output["evaluator_configs"] = [
            evaluator_config.to_dict() for evaluator_config in output.pop("evaluator_configs")
        ]
        return output
