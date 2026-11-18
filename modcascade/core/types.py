from typing import Literal, Protocol

from pydantic import BaseModel, Field

Label = Literal["ok", "spam", "toxic", "contacts", "prohibited", "fraud"]
Stage = Literal["rules", "classifier", "llm"]


class Decision(BaseModel):
    verdict: Literal["approve", "reject", "escalate"]
    label: Label
    confidence: float = Field(ge=0, le=1)
    reason: str | None = None
    stage: Stage


class Moderator(Protocol):
    async def moderate_batch(self, texts: list[str]) -> list[Decision | None]:
        """Return one result per text in input order. None defers to the next stage."""
        ...
