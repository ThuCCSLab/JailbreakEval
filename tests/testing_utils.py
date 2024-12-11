# %%
import uuid
import datetime
from typing import Any, Generator, List, Union
from unittest.mock import patch
from openai.types import CompletionUsage, ModerationCreateResponse
from openai.types.chat import ChatCompletionMessage
from openai.types.chat.chat_completion import ChatCompletion, Choice
from openai.types.moderation import Moderation, Categories, CategoryScores, CategoryAppliedInputTypes
from transformers.pipelines import TextGenerationPipeline, TextClassificationPipeline
from transformers import PreTrainedModel

patch_openai_chat_create = patch("openai.resources.chat.Completions.create")

patch_openai_moderation_create = patch("openai.resources.Moderations.create")

patch_transformers_pipeline_factory = patch("transformers.pipelines.__init__.pipeline")

patch_chat_service_pipeline_factory = patch(
    "jailbreakeval.services.chat.transformers_pipeline_service.pipeline_factory"
)
patch_text_classification_service_pipeline_factory = patch(
    "jailbreakeval.services.text_classification.transformers_pipeline_service.pipeline_factory"
)
patch_transformers_chat_pipeline_call = patch("transformers.pipelines.text_generation.TextGenerationPipeline.__call__")
patch_transformers_classification_pipeline_call = patch(
    "transformers.pipelines.text_classification.TextClassificationPipeline.__call__"
)


class DummyModel(PreTrainedModel):
    def __init__(self):
        self.name_or_path = "dummy"


class DummyTextClassificationPipeline(TextClassificationPipeline):
    def __init__(self):
        self.model = DummyModel()

    def __call__(self, inputs, **kwargs):
        return super().__call__(inputs=inputs, **kwargs)


class DummyTextGenerationPipeline(TextGenerationPipeline):
    def __init__(self):
        self.model = DummyModel()

    def __call__(self, text_inputs, **kwargs):
        return super().__call__(text_inputs=text_inputs, **kwargs)


def openai_chat_completions(response: Union[str, List[str]]) -> Generator[ChatCompletion, Any, None]:
    if isinstance(response, str):
        response = [response]
    chat_id = str(uuid.uuid4())
    for i, response in enumerate(response):
        yield ChatCompletion(
            id=f"mock-{chat_id}-{i}",
            model="mock-model",
            object="chat.completion",
            usage=CompletionUsage(completion_tokens=1, prompt_tokens=2, total_tokens=3),
            choices=[
                Choice(
                    finish_reason="stop",
                    index=0,
                    message=ChatCompletionMessage(
                        content=response,
                        role="assistant",
                    ),
                )
            ],
            created=int(datetime.datetime.now().timestamp()),
        )


def openai_moderations(response: Union[bool, List[bool]]):
    if isinstance(response, bool):
        response = [response]
    chat_id = str(uuid.uuid4())
    for i, response in enumerate(response):
        yield ModerationCreateResponse(
            id=f"mock-{chat_id}-{i}",
            model="mock-model",
            results=[
                Moderation(
                    flagged=response,
                    category_applied_input_types=CategoryAppliedInputTypes.construct(),
                    categories=Categories.construct(),
                    category_scores=CategoryScores.construct(),
                )
            ],
        )


def transformers_chat_pipeline_response(
    response: Union[str, List[str]],
) -> Generator[List[dict[str, Any]], Any, None]:
    if isinstance(response, str):
        response = [response]
    chat_id = str(uuid.uuid4())
    for i, response in enumerate(response):
        yield [{"mock_id": f"mock-{chat_id}-{i}", "generated_text": response}]


# %%
