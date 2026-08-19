"""Pytest configuration and fixtures for LLMZ80 tests."""


class FakeMessageStream:
    """What `client.messages.stream` returns, for tests that fake a model.

    `llmz80.studio.llm.structured` streams every request -- the SDK refuses a
    non-streaming call whose `max_tokens` could outlast ten minutes -- so a
    fake client answers with this rather than with a message directly. It is
    the whole contract `structured` uses: a context manager whose
    `get_final_message` hands back the response (or raises what it was given,
    the way the SDK's own post-parse validation does).
    """

    def __init__(self, outcome) -> None:
        self.outcome = outcome

    def __enter__(self) -> "FakeMessageStream":
        return self

    def __exit__(self, *_) -> bool:
        return False

    def get_final_message(self):
        if isinstance(self.outcome, Exception):
            raise self.outcome
        return self.outcome


def fake_message(parsed, **extra):
    """A stand-in response carrying `parsed` as its `parsed_output`."""
    return type("Response", (), {"parsed_output": parsed, **extra})()
