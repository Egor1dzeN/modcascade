from fastapi import FastAPI
from pydantic import BaseModel, Field

from modcascade.core.types import Decision, Moderator
from modcascade.moderators.dummy import DummyModerator
from modcascade.serving.cascade import Cascade


class ModerateRequest(BaseModel):
    texts: list[str] = Field(min_length=1)


class ModerateResponse(BaseModel):
    decisions: list[Decision | None]


def create_app(moderator: Moderator) -> FastAPI:
    app = FastAPI(title="modcascade")

    @app.post("/moderate")
    async def moderate(request: ModerateRequest) -> ModerateResponse:
        return ModerateResponse(decisions=await moderator.moderate_batch(request.texts))

    return app


app = create_app(
    Cascade(
        [
            DummyModerator(
                {
                    "Message me on Telegram": Decision(
                        verdict="reject", label="contacts", confidence=1, stage="rules"
                    )
                }
            ),
            DummyModerator(
                {
                    "Great service": Decision(
                        verdict="approve", label="ok", confidence=1, stage="classifier"
                    )
                }
            ),
            DummyModerator(
                {
                    "I promise to double your deposit": Decision(
                        verdict="escalate",
                        label="fraud",
                        confidence=1,
                        reason="Flagged for manual review in this demo.",
                        stage="llm",
                    )
                }
            ),
        ]
    )
)
