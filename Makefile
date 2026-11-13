PY := .venv/bin/python
.PHONY: setup data test
setup:
	python3 -m venv .venv && .venv/bin/pip install -q -e "pipeline[dev]"
data:
	cd pipeline && ../$(PY) -m worldatlas build
test:
	cd pipeline && ../$(PY) -m pytest -q -m "not network"
