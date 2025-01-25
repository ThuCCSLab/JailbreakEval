import contextlib
import gc
from typing import Any, Dict, Tuple
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import torch

from jailbreakeval.configurations.chat_configuration import ChatJailbreakEvaluatorConfig
from jailbreakeval.configurations.configuration_base import JailbreakEvaluatorConfig
from jailbreakeval.configurations.text_classifier_configuration import TextClassificationJailbreakEvaluatorConfig
from jailbreakeval.configurations.voting_configuration import VotingJailbreakEvaluatorConfig
from jailbreakeval.evaluators.chat_evaluator import ChatJailbreakEvaluator
from jailbreakeval.evaluators.evaluator_base import JailbreakEvaluator
from jailbreakeval.evaluators.voting_evaluator import VotingJailbreakEvaluator
from jailbreakeval.services.chat.openai_service import OpenAIChatService
import yaml
from pathlib import Path
import click
import pandas as pd
import json
import logging
import time
from prettytable import PrettyTable

logger = logging.getLogger(__name__)


def bench_to_file(evaluator: JailbreakEvaluator, data, output):  # -> Any:
    print(evaluator.name_or_path)
    results = evaluator(data)
    Path(output).write_text(json.dumps(results))
    return results


def load_evaluator(evaluator_id: str, config) -> JailbreakEvaluator:
    evaluator_config = JailbreakEvaluatorConfig.from_preset(evaluator_id)
    patch_config(config, evaluator_config)
    return JailbreakEvaluator.from_config(evaluator_config)


def patch_config(config: Dict[str, Any], evaluator_config: JailbreakEvaluatorConfig):
    if isinstance(evaluator_config, ChatJailbreakEvaluatorConfig):
        patch_chat_config(config, evaluator_config)
    elif isinstance(evaluator_config, TextClassificationJailbreakEvaluatorConfig):
        patch_text_classification_config(config, evaluator_config)
    elif isinstance(evaluator_config, VotingJailbreakEvaluatorConfig):
        for evaluator_conf in evaluator_config.evaluator_configs:
            patch_config(config, evaluator_conf)


def patch_text_classification_config(
    config: Dict[str, Any], evaluator_config: TextClassificationJailbreakEvaluatorConfig
):
    if evaluator_config.text_classification_service_type == "transformers-pipeline":
        model_kwargs = {}
        with contextlib.suppress(KeyError):
            model_kwargs |= config["transformers"]["common"]
        with contextlib.suppress(KeyError):
            model_kwargs |= config["transformers"][evaluator_config.text_classification_model]
        if "name_or_path" in model_kwargs:
            evaluator_config.text_classification_model = model_kwargs.pop("name_or_path")
        evaluator_config.text_classification_service_kwargs.update(model_kwargs)
    elif evaluator_config.text_classification_service_type == "openai":
        evaluator_config.text_classification_service_kwargs.update(config.get("openai", {}))
    elif evaluator_config.text_classification_service_type == "perspective":
        evaluator_config.text_classification_service_kwargs.update(config.get("perspective", {}))


def patch_chat_config(config: Dict[str, Any], evaluator_config: ChatJailbreakEvaluatorConfig):
    if evaluator_config.chat_service_type == "openai":
        evaluator_config.chat_service_kwargs.update(config.get("openai", {}))
    elif evaluator_config.chat_service_type == "transformers-pipeline":
        model_kwargs = {}
        with contextlib.suppress(KeyError):
            model_kwargs |= config["transformers"]["common"]
        with contextlib.suppress(KeyError):
            model_kwargs |= config["transformers"][evaluator_config.chat_model]
        if "name_or_path" in model_kwargs:
            evaluator_config.chat_model = model_kwargs.pop("name_or_path")
        evaluator_config.chat_service_kwargs.update(model_kwargs)


def load_csv_dataset(filepath):
    dataset = pd.read_csv(filepath, dtype={"question": "string", "answer": "string", "label": "boolean"})

    if "question" not in dataset:
        raise ValueError("Dataset missing column `question`.")

    if "answer" not in dataset:
        raise ValueError("Dataset missing column `answer`.")

    dataset = dataset.fillna(value={"question": "", "answer": ""})

    if "label" not in dataset:
        dataset["label"] = pd.NA
        dataset["label"] = dataset["label"].astype("boolean")
    return dataset


def eval_metrics(labels, preds):
    labels = pd.Series(labels, dtype="boolean")
    preds = pd.Series(preds, dtype="boolean")
    non_na_preds = ~preds.isna()
    non_na_labels = ~labels.isna()
    non_na_intersected = non_na_labels & non_na_preds
    metrics = {
        "coverage": non_na_preds.mean(),
        "jailbreak_ratio": preds[non_na_preds].mean(),
    }
    if any(non_na_labels):
        metrics["labelled_coverage"] = non_na_intersected.sum() / non_na_labels.sum()
    if any(non_na_intersected):
        y_true = labels[non_na_intersected]
        y_pred = preds[non_na_intersected]
        metrics |= {
            "accuracy": accuracy_score(y_true, y_pred),
            "recall": recall_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred),
            "f1": f1_score(y_true, y_pred),
        }
    return metrics


@click.command()
@click.argument("evaluators", nargs=-1)
@click.option("--dataset", "dataset_filepath", required=True, help="Path to a CSV file containing jailbreak attempts.")
@click.option("--config", "config_filepath", help="The path to a YAML configuration file.")
@click.option("--output", "output_filepath", help="The path to save evaluation details in JSON.")
def main(
    evaluators: Tuple[str],
    dataset_filepath: str,
    output_filepath: str = "",
    config_filepath: str = "",
) -> None:
    if config_filepath and Path(config_filepath).is_file():
        config = yaml.safe_load(Path(config_filepath).read_text())
    else:
        config = {}

    dataset = load_csv_dataset(dataset_filepath)

    labels = dataset["label"].astype("O").replace(pd.NA, None).to_list()

    results = {
        "Annotation": {
            "preds": labels,
            **eval_metrics(
                pd.Series([None] * len(dataset["label"]), dtype="boolean"),
                dataset["label"],
            ),
        }
    }

    for evaluator_id in evaluators:
        try:
            evaluator = load_evaluator(evaluator_id, config)
            if evaluator.name_or_path in results:
                logger.warning(
                    f"Skipping {evaluator_id} because the associated evaluator {evaluator.name_or_path} has been loaded."
                )
                continue
            start_time = time.perf_counter_ns()
            preds = evaluator(dataset.to_dict("records"))
            end_time = time.perf_counter_ns()

            elapsed_time_ms = (end_time - start_time) // 1000000

            results[evaluator.name_or_path] = {
                "preds": preds,
                **eval_metrics(labels, preds),
                "time_ms": elapsed_time_ms,
            }
            if isinstance(evaluator, VotingJailbreakEvaluator):
                prompt_tokens_usage, completion_tokens_usage = 0, 0
                for sub_evaluator in evaluator.evaluators:
                    if isinstance(sub_evaluator, ChatJailbreakEvaluator) and isinstance(
                        sub_evaluator.chat_service, OpenAIChatService
                    ):
                        prompt_tokens_usage += sub_evaluator.chat_service.prompt_tokens_usage
                        completion_tokens_usage += sub_evaluator.chat_service.completion_tokens_usage
                results[evaluator.name_or_path] |= {
                    "prompt_tokens_usage": prompt_tokens_usage,
                    "completion_tokens_usage": completion_tokens_usage,
                }
            if isinstance(evaluator, ChatJailbreakEvaluator) and isinstance(evaluator.chat_service, OpenAIChatService):
                results[evaluator.name_or_path] |= {
                    "model": evaluator.chat_service.model,
                    "prompt_tokens_usage": evaluator.chat_service.prompt_tokens_usage,
                    "completion_tokens_usage": evaluator.chat_service.completion_tokens_usage,
                }

            del evaluator
        except Exception as e:
            logger.error(f"Failed to evaluate {evaluator_id}: {e}")
        finally:
            gc.collect()
            torch.cuda.empty_cache()

    if output_filepath:
        with open(output_filepath, "w") as f:
            json.dump(results, f, indent=2)
    print("Dataset:", dataset_filepath)
    print("Dataset size:", len(dataset))
    print("Evaluation result:")
    tb = PrettyTable(["name", "coverage", "ASR", "time (ms)", "prompt_tokens", "completion_tokens"])
    tb.float_format = ".2"
    for k, v in results.items():
        tb.add_row(
            [k, v["coverage"], v["jailbreak_ratio"]]
            + [v.get("time_ms", "N/A"), v.get("prompt_tokens_usage", "N/A"), v.get("completion_tokens_usage", "N/A")]
        )
    print(tb)
    print("Evaluation agreement with annotation:")
    tb = PrettyTable(["name", "coverage", "accuracy", "recall", "precision", "f1"])
    tb.float_format = ".2"
    for k, v in results.items():
        if k != "Annotation":
            tb.add_row([k, v["labelled_coverage"], v["accuracy"], v["recall"], v["precision"], v["f1"]])
    print(tb)


if __name__ == "__main__":
    main()
