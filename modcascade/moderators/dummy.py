from collections.abc import Mapping

from modcascade.core.types import Decision


class DummyModerator:
    def __init__(self, decisions: Mapping[str, Decision]) -> None:
        self._decisions = dict(decisions)

    async def moderate_batch(self, texts: list[str]) -> list[Decision | None]:
        return [self._decisions.get(text) for text in texts]
