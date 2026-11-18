# modcascade

modcascade is a moderation service for Russian-language user-generated content. The demo runs an HTTP request through a cascade of rules, a classifier, and an LLM. Each stage receives only the texts that earlier stages deferred.

## Run locally

On Windows, double-click [run.bat](run.bat) or run `.\run.bat` from the project root. The script requires Python 3.11 or later. It creates `.venv` on first launch and installs missing dependencies from PyPI. Press Ctrl+C to stop the server.

To install development tools and start the server manually, run these commands in PowerShell.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m uvicorn modcascade.api.main:app --reload
```

If you have Make installed, activate `.venv` and run `make serve`.

To try this request, open `POST /moderate` in [Swagger UI](http://127.0.0.1:8000/docs).

```json
{
  "texts": [
    "Message me on Telegram",
    "Great service",
    "I promise to double your deposit",
    "New text"
  ]
}
```

The response lists `decisions` in input order. The stub moderators match exact strings to predefined decisions.

| Text | Stage | Decision |
| --- | --- | --- |
| Message me on Telegram | `rules` | `reject`, `contacts` |
| Great service | `classifier` | `approve`, `ok` |
| I promise to double your deposit | `llm` | `escalate`, `fraud` |
| New text | | `null` |

`escalate` recommends manual review. A `null` result means every stage deferred the text.

## Integration points

- The [moderator contract](modcascade/core/types.py) defines `Decision`, the preliminary label set, and the `Moderator` protocol. `moderate_batch` returns one result per input text in the original order. A `None` result defers the text to the next stage.
- The [cascade](modcascade/serving/cascade.py) runs the supplied moderators in order. The [FastAPI entry point](modcascade/api/main.py) configures three `DummyModerator` instances for the demo. Edit that list to replace, add, or reorder moderators.
- `modcascade/data/` is for data preparation, and `modcascade/training/` is for model training.

### Dataset format

Store processed datasets in `data/processed/*.parquet`.

| Field | Type | Values or example |
| --- | --- | --- |
| `id` | `str` | `avito_000123` |
| `text` | `str` | Selling a phone |
| `label` | `str` | `ok`, `spam`, `toxic`, `contacts`, `prohibited`, `fraud` |
| `source` | `str` | `avito`, `toxic_2ch`, `geo_reviews`, `synthetic` |
| `split` | `str` | `train`, `val`, `test` |

Keep datasets and model weights in local or external storage.

## Checks

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m pytest
```

GitHub Actions runs the same checks. The integration test sends a batch to FastAPI and verifies response order, decisions from all three stages, and the result when every stage defers a text.
