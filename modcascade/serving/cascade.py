from collections.abc import Sequence

from modcascade.core.types import Decision, Moderator


class Cascade:
    def __init__(self, moderators: Sequence[Moderator]) -> None:
        self._moderators = tuple(moderators)

    async def moderate_batch(self, texts: list[str]) -> list[Decision | None]:
        decisions: list[Decision | None] = [None] * len(texts)
        pending = list(range(len(texts)))

        for moderator in self._moderators:
            if not pending:
                break

            batch = [texts[index] for index in pending]
            results = await moderator.moderate_batch(batch)
            if len(results) != len(batch):
                raise ValueError(
                    f"{type(moderator).__name__} returned {len(results)} results "
                    f"for {len(batch)} texts"
                )

            deferred = []
            for index, decision in zip(pending, results, strict=True):
                if decision is None:
                    deferred.append(index)
                else:
                    decisions[index] = decision
            pending = deferred

        return decisions
