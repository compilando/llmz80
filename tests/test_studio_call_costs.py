"""What each of the ten call sites is worth, asserted in one place.

Every structured call in Studio used to be sent the same way: `effort` left
out, so the model reasoned at its `high` default, and `max_tokens` left at
`DEFAULT_MAX_TOKENS` -- 64000 -- whether the answer was a whole C program or a
boolean verdict. An 8x8 tile of eight pen characters was asked for with the
same deliberation and the same room as `generator.ProgramSources`.

That is what a survey of `studio-projects/*/studio.log` found the money going
on. `llm.py` had said as much for months, in the docstring on its own `effort`
parameter -- *"a caller passes one only to spend less: drawing an 8x8 tile
does not need the reasoning that writing a whole C program does"* -- and no
caller ever passed one.

The assertions live together rather than one per collaborator's own test file
because the thing worth protecting is the *relation* between them: the writer
is the expensive call and everything else is cheaper than it. Spread across
ten files, that shape is invisible and the next call site added defaults
quietly back to 64000 at `high`.
"""

from pathlib import Path

import pytest

from llmz80.studio.models import TargetPlatform
from llmz80.studio.samples import blank_project
from tests.conftest import FakeMessageStream, fake_message


class _Recorder:
    """A client that answers anything and remembers how it was asked."""

    def __init__(self, answer):
        self.answer = answer
        self.calls = []
        self.messages = self
        self.beta = type("Beta", (), {"messages": self})()

    def stream(self, **kwargs):
        self.calls.append(kwargs)
        return FakeMessageStream(fake_message(self.answer))


def _project():
    return blank_project("Costed", TargetPlatform.SPECTRUM)


def _grid():
    from llmz80.studio.sprite_grid import SpriteFrameGrid, SpriteSheetGrid

    return SpriteSheetGrid(frames=[SpriteFrameGrid(rows=["0" * 16] * 16)])


@pytest.fixture
def sprite_call():
    from llmz80.studio.sprite_artist import ClaudeGridSheetSource

    project = _project()
    client = _Recorder(_grid())
    source = ClaudeGridSheetSource(client)
    source.draw(project, "draw the actor", frames=1)
    return client.calls[0]


@pytest.fixture
def tile_call():
    from llmz80.studio.sprite_artist import ClaudeGridTileSource

    project = _project()
    client = _Recorder(_grid())
    source = ClaudeGridTileSource(client)
    source.draw(project, "draw the wall")
    return client.calls[0]


@pytest.fixture
def coherence_call():
    from llmz80.studio.design_exam import DesignCoherence, ResponsesCoherenceExaminer

    client = _Recorder(
        DesignCoherence(coherent=True, missing_entities=[], missing_tiles=[], quoted="")
    )
    ResponsesCoherenceExaminer(client).examine(_project())
    return client.calls[0]


@pytest.fixture
def coverage_call():
    from llmz80.studio.design_exam import BriefCoverage, ResponsesDesignExaminer

    client = _Recorder(BriefCoverage(covered=True, missing=[], quoted=""))
    ResponsesDesignExaminer(client).examine(_project())
    return client.calls[0]


@pytest.fixture
def runtime_exam_call():
    from llmz80.studio.runtime_exam import ResponsesRuntimeExaminer, RuntimeExam

    client = _Recorder(RuntimeExam(assertions=[], unverifiable=[]))
    ResponsesRuntimeExaminer(client).examine(_project(), [], ["g_state"])
    return client.calls[0]


@pytest.fixture
def research_call():
    from llmz80.studio.reference import GameReference, ResponsesReferenceResearcher

    client = _Recorder(GameReference(identified=False, confidence="low"))
    ResponsesReferenceResearcher(client).research("a maze game", "spectrum")
    return client.calls[0]


@pytest.fixture
def writer_call(tmp_path: Path):
    from llmz80.studio.generator import ProgramFile, ProgramSources, ResponsesProgramWriter

    client = _Recorder(
        ProgramSources(summary="s", files=[ProgramFile(name="main.c", body="int main(){}")])
    )
    ResponsesProgramWriter(client).write(_project())
    return client.calls[0]


CHEAP = ("sprite_call", "tile_call", "coherence_call", "coverage_call", "runtime_exam_call")


@pytest.mark.parametrize("call", CHEAP)
def test_a_cheap_answer_does_not_pay_for_the_writers_deliberation(call, request):
    """Nothing on this list writes a program, so nothing on it reasons like one.

    `high` is the model's own default, so leaving `effort` out is not neutral
    -- it is the most expensive setting, chosen by omission.
    """
    kwargs = request.getfixturevalue(call)

    assert kwargs["output_config"]["effort"] in ("low", "medium")


@pytest.mark.parametrize("call", CHEAP)
def test_a_cheap_answer_is_not_given_the_room_to_write_a_program(call, request):
    """`max_tokens` bounds thinking too, and thinking is what gets billed.

    A ceiling is not the price of an ordinary answer -- an answer that takes a
    hundred tokens is charged for a hundred. It is the price of the worst
    answer, and 64000 tokens of deliberation over an 8x8 tile is a real
    outcome, not a hypothetical one.
    """
    kwargs = request.getfixturevalue(call)

    assert kwargs["max_tokens"] < 64000


def test_the_writer_keeps_the_room_and_the_reasoning_it_needs(writer_call):
    """The one call worth paying full price for.

    Every attempt it takes is one the compiler already refused; a cheaper
    program is a false economy measured in further attempts.
    """
    assert writer_call["max_tokens"] == 64000
    assert "effort" not in writer_call.get("output_config", {})


def test_the_writer_is_told_how_much_the_whole_job_is_worth(writer_call):
    """Truncation is the expensive failure, not slowness.

    `cesar-mondongo-basket` attempt 3: 25 minutes, then `EOF while parsing a
    string at line 1 column 21706`. A task budget is the only thing the model
    can actually see and pace itself against -- `max_tokens` cuts it off
    wherever it happens to be.
    """
    assert writer_call["output_config"]["task_budget"]["type"] == "tokens"
    assert writer_call["betas"] == ["task-budgets-2026-03-13"]


def test_the_writers_invariant_half_travels_as_a_cached_prefix(writer_call):
    """About 10 600 of the writer's 15 500 prompt tokens are the same on every
    attempt -- the platform library, the retrieved examples, the platform
    notes -- and were re-billed in full five times a run."""
    system = writer_call["system"]

    assert isinstance(system, list)
    assert system[-1]["cache_control"] == {"type": "ephemeral", "ttl": "1h"}
    assert len(system[-1]["text"]) > 4000


def test_research_reasons_less_than_a_design_does(research_call):
    """The web search does the work here; the model summarises what came back."""
    assert research_call["output_config"]["effort"] == "medium"
    assert research_call["max_tokens"] < 64000
