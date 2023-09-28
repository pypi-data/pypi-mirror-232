# Copyright (c) 2023, Justin Béra (@just1not2) <me@just1not2.org>
# Apache License 2.0 (see LICENSE or https://www.apache.org/licenses/LICENSE-2.0.txt


default: build

.env:
	cp .env.template .env

.PHONY: build
build: env
	env/bin/python3 -m build

env:
	python3 -m venv env
	env/bin/python3 -m pip install --upgrade pip
	env/bin/python3 -m pip install -r dev-requirements.txt

.PHONY: lint
lint: env
	env/bin/pylint jon

.PHONY: test
test: env
	PYTHONPATH=$(CURDIR)/jon:$${PYTHONPATH} env/bin/python3 tests/main.py

.PHONY: upload
upload:
	source .env && env/bin/python3 -m twine upload --username __token__ --password $${PYPI_TOKEN} dist/*
