from openai import OpenAI
from jailbreakeval.services.chat.openai_service import OpenAIChatService
from jailbreakeval.services.chat.service_base import ChatServiceFactory
from tests.testing_utils import patch_openai_chat_create, openai_chat_completions


def test_init():
    # by arg
    service = OpenAIChatService(model="foo", api_key="bar")
    assert service.model == "foo"
    assert service.client.api_key == "bar"

    # by factory
    service = ChatServiceFactory.build("openai", model="foo", api_key="bar")
    assert isinstance(service, OpenAIChatService)
    assert service.model == "foo"
    assert service.client.api_key == "bar"

    # by arg, use existing client
    client = OpenAI(api_key="baz")

    service = OpenAIChatService(client=client, model="foo", api_key="ignored")
    assert service.model == "foo"
    assert service.client is client
    assert service.client.api_key == "baz"

    # by factory, use existing client
    service = ChatServiceFactory.build("openai", client=client, model="foo", api_key="ignored")
    assert isinstance(service, OpenAIChatService)
    assert service.model == "foo"
    assert service.client is client
    assert service.client.api_key == "baz"


@patch_openai_chat_create
def test_chat(openai_chat_mock):
    MESSAGES = [{"role": "user", "content": "Hello."}]
    MODEL = "gpt-3.5-turbo"
    RESPONSE = "This is a mock response, how can I help you?"

    openai_chat_mock.side_effect = openai_chat_completions([RESPONSE] * 4)

    # normal
    service = OpenAIChatService(model=MODEL, api_key="foo")
    response = service.chat(MESSAGES)

    openai_chat_mock.assert_called_with(model=MODEL, messages=MESSAGES)
    assert isinstance(response, str)
    assert response == RESPONSE
    assert service.prompt_tokens_usage > 0
    assert service.completion_tokens_usage > 0

    # override
    response = service.chat(MESSAGES, key="value")

    openai_chat_mock.assert_called_with(model=MODEL, messages=MESSAGES, key="value")
    assert isinstance(response, str)
    assert response == RESPONSE
    assert service.prompt_tokens_usage > 0
    assert service.completion_tokens_usage > 0

    # gen_kwargs
    service = OpenAIChatService(model=MODEL, api_key="foo", chat_kwargs={"hello": "world", "foo": "bar"})
    response = service.chat(MESSAGES)

    openai_chat_mock.assert_called_with(model=MODEL, messages=MESSAGES, hello="world", foo="bar")
    assert isinstance(response, str)
    assert response == RESPONSE
    assert service.prompt_tokens_usage > 0
    assert service.completion_tokens_usage > 0

    # gen_kwargs + override
    response = service.chat(MESSAGES, foo="baz", key="value")

    openai_chat_mock.assert_called_with(model=MODEL, messages=MESSAGES, hello="world", foo="baz", key="value")
    assert isinstance(response, str)
    assert response == RESPONSE
    assert service.prompt_tokens_usage > 0
    assert service.completion_tokens_usage > 0
