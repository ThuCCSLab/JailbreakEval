from openai import OpenAI
from jailbreakeval.services.text_classification.opeai_service import OpenAITextClassificationService
from jailbreakeval.services.text_classification.service_base import TextClassificationServiceFactory
from tests.testing_utils import patch_openai_moderation_create, openai_moderations


def test_init():
    service = OpenAITextClassificationService(model="foo", api_key="bar")
    assert service.model == "foo"
    assert service.client.api_key == "bar"

    service = TextClassificationServiceFactory.build("openai", model="foo", api_key="bar")
    assert isinstance(service, OpenAITextClassificationService)
    assert service.model == "foo"
    assert service.client.api_key == "bar"

    client = OpenAI(api_key="baz")

    service = OpenAITextClassificationService(client=client, model="foo", api_key="ignored")
    assert service.model == "foo"
    assert service.client is client
    assert service.client.api_key == "baz"

    service = TextClassificationServiceFactory.build("openai", client=client, model="foo", api_key="ignored")
    assert isinstance(service, OpenAITextClassificationService)
    assert service.model == "foo"
    assert service.client is client
    assert service.client.api_key == "baz"


@patch_openai_moderation_create
def test_predict(mock_openai_moderation_create):
    mock_openai_moderation_create.side_effect = openai_moderations([True] * 4)
    client = OpenAI(api_key="foo")
    MODEL = "text-moderation-stable"
    service = OpenAITextClassificationService(client=client, model=MODEL)
    TEXT = "I want to kill myself."
    response = service.predict(TEXT)
    mock_openai_moderation_create.assert_called_with(model=MODEL, input=TEXT)
    assert isinstance(response, dict)
    assert "flagged" in response
    assert isinstance(response["flagged"], bool)
    assert response["flagged"]

    response = service.predict(TEXT, key="value")
    mock_openai_moderation_create.assert_called_with(model=MODEL, input=TEXT, key="value")
    assert isinstance(response, dict)
    assert "flagged" in response
    assert isinstance(response["flagged"], bool)
    assert response["flagged"]

    service = OpenAITextClassificationService(
        client=client, model=MODEL, predict_kwargs={"hello": "world", "foo": "bar"}
    )
    response = service.predict(TEXT)
    mock_openai_moderation_create.assert_called_with(model=MODEL, input=TEXT, hello="world", foo="bar")
    assert isinstance(response, dict)
    assert "flagged" in response
    assert isinstance(response["flagged"], bool)
    assert response["flagged"]

    response = service.predict(TEXT, foo="baz", key="value")
    mock_openai_moderation_create.assert_called_with(model=MODEL, input=TEXT, hello="world", foo="baz", key="value")
    assert isinstance(response, dict)
    assert "flagged" in response
    assert isinstance(response["flagged"], bool)
    assert response["flagged"]
