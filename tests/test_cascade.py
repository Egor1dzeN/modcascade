import asyncio

import pytest

from modcascade.core.types import Decision
from modcascade.serving.cascade import Cascade


class RecordingModerator:
    def __init__(self, results: list[Decision | None]) -> None:
        self.results = results
        self.batches: list[list[str]] = []

    async def moderate_batch(self, texts: list[str]) -> list[Decision | None]:
        self.batches.append(texts)
        return self.results


def test_only_deferred_texts_reach_later_stages() -> None:
    reject = Decision(verdict="reject", label="contacts", confidence=1, stage="rules")
    approve = Decision(verdict="approve", label="ok", confidence=1, stage="classifier")
    rules = RecordingModerator([None, reject])
    classifier = RecordingModerator([approve])
    llm = RecordingModerator([])
    cascade = Cascade([rules, classifier, llm])

    result = asyncio.run(cascade.moderate_batch(["review", "contact"]))

    assert result == [approve, reject]
    assert rules.batches == [["review", "contact"]]
    assert classifier.batches == [["review"]]
    assert llm.batches == []


def test_cascade_can_reach_a_fourth_moderator() -> None:
    approve = Decision(verdict="approve", label="ok", confidence=1, stage="llm")
    moderators = [RecordingModerator([None]) for _ in range(3)]
    moderators.append(RecordingModerator([approve]))

    result = asyncio.run(Cascade(moderators).moderate_batch(["review"]))

    assert result == [approve]
    assert all(moderator.batches == [["review"]] for moderator in moderators)


def test_mismatched_result_count_fails() -> None:
    rules = RecordingModerator([])
    classifier = RecordingModerator([])
    cascade = Cascade([rules, classifier])

    with pytest.raises(ValueError, match="returned 0 results for 1 texts"):
        asyncio.run(cascade.moderate_batch(["text"]))

    assert classifier.batches == []
