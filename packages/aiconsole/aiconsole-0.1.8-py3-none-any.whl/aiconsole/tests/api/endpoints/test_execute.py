from fastapi.testclient import TestClient
from pytest_mock import MockFixture

from aiconsole.api.schema import GptHTTPRequest
from aiconsole.gpt.consts import GPTMode


# TODO move it to common testing tools
class AsyncIteratorMock:
    def __init__(self, data):
        self.data = data

    def __aiter__(self):
        return self

    async def __anext__(self):
        if len(self.data) == 0:
            raise StopAsyncIteration
        return self.data.pop(0)


def test_gpt_endpoint_streaming(client: TestClient, mocker: MockFixture):
    stream_text = "++RESPONSE++"

    class StrategyMock:
        def execution_mode(self, context):  # noqa
            return AsyncIteratorMock([stream_text])

    payload = GptHTTPRequest(
        strategy="test_strategy", mode=GPTMode.FAST, messages=[], relevant_manuals=[]
    )

    mocker.patch("aiconsole.api.endpoints.execute.ExecutionTaskContext")

    mocker.patch.dict(
        "aiconsole.api.endpoints.execute.strategies.strategies",
        {"test_strategy": StrategyMock()},
    )

    response = client.post("/execute", json=payload.model_dump())
    assert response.status_code == 200
    assert response.text == stream_text
