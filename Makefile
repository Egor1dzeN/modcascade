.PHONY: serve lint test

PYTHON ?= python

serve:
	$(PYTHON) -m uvicorn modcascade.api.main:app --reload

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

test:
	$(PYTHON) -m pytest
