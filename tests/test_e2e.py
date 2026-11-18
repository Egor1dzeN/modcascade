import asyncio

import httpx
import pytest

from modcascade.api.main import app


async def post_moderate(payload: dict) -> httpx.Response:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.post("/moderate", json=payload)


def test_moderate_batch_through_all_stages() -> None:
    response = asyncio.run(
        post_moderate(
            {
                "texts": [
                    "I promise to double your deposit",
                    "Message me on Telegram",
                    "New text",
                    "Great service",
                    "Message me on Telegram",
                ]
            }
        )
    )

    assert response.status_code == 200
    decisions = response.json()["decisions"]
    assert [
        (item["stage"], item["verdict"], item["label"]) if item else None
        for item in decisions
    ] == [
        ("llm", "escalate", "fraud"),
        ("rules", "reject", "contacts"),
        None,
        ("classifier", "approve", "ok"),
        ("rules", "reject", "contacts"),
    ]
    assert decisions[0]["reason"] == "Flagged for manual review in this demo."


@pytest.mark.parametrize("payload", [{}, {"texts": []}, {"texts": [1]}])
def test_moderate_rejects_invalid_payload(payload: dict) -> None:
    response = asyncio.run(post_moderate(payload))

    assert response.status_code == 422
