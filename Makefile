# Local checks (replaces the former GitHub Actions CI).
#   make install   create .venv and install deps
#   make check     lint + test + smoke   (run automatically on `git push` after `make hooks`)
#   make hooks     enable .githooks/pre-push
#
# Override the interpreter used for lint/test/smoke:   make check PYTHON=python3.12
# Override the interpreter used to create the venv:    make install BOOTSTRAP_PYTHON=python3.12

PYTHON ?= .venv/bin/python
# Interpreter used only to create .venv (needs Python >= 3.10). First of these found on PATH.
BOOTSTRAP_PYTHON ?= $(shell for p in python3.12 python3.11 python3.10 python3; do command -v $$p >/dev/null 2>&1 && { echo $$p; break; }; done)
SMOKE_OUT ?= $(or $(TMPDIR),/tmp)

.PHONY: install lint test smoke check hooks

install:
	$(BOOTSTRAP_PYTHON) -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install -r requirements.txt -r requirements-dev.txt

lint:
	$(PYTHON) -m ruff check vpt/ tests/

test:
	$(PYTHON) -m pytest tests/ -v --tb=short

smoke:
	$(PYTHON) -m vpt.cli --version
	$(PYTHON) -m vpt.cli adapters
	$(PYTHON) -m vpt.cli detect -s sample_data/auburn_dental_benco.csv
	$(PYTHON) -m vpt.cli analyze \
		-s sample_data/sample_clinic_vetcove.csv \
		-c sample_data/vet_catalog.csv \
		-o $(SMOKE_OUT)/vet_results.json
	test -s $(SMOKE_OUT)/vet_results.json

check: lint test smoke

hooks:
	git config core.hooksPath .githooks
	@echo "git hooks enabled: .githooks/pre-push runs 'make check'"
