# This makefile copied from https://github.com/rochacbruno/fastapi-project-template/blob/main/Makefile
.ONESHELL:
# ENV_PREFIX=$(shell python -c "if __import__('pathlib').Path('.venv/bin/pip').exists(): print('.venv/bin/')")
USING_POETRY=$(shell grep "tool.poetry" pyproject.toml && echo "yes")

.PHONY: help
help:             ## Show the help.
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@fgrep "##" Makefile | fgrep -v fgrep


.PHONY: show
show:             ## Show the current python environment.
	@echo "Current environment:"
	@echo "Running using "
	@python -V
	@python -m site

.PHONY: install-precommit-hooks
install-precommit-hooks:          ## Installs the pre-commit hooks
	@pre-commit install --install-hooks

.PHONY: requirements-prod
requirements-prod:          ## Install the project dependencies in dev mode.
	@echo "Don't forget to run 'make virtualenv' if you got errors."
	pip install -r app/requirements.txt

.PHONY: requirements
requirements: requirements-prod      ## Install the project dependencies in dev mode.
	pip install -r app/requirements-dev.txt

.PHONY: reinstall-dev-requirements
reinstall-dev-requirements:          ## Uninstall and install the project dependencies in dev mode.
	pre-commit clean
	pre-commit gc
	pre-commit uninstall
	pip freeze | xargs pip uninstall -y
	make requirements
	make install-precommit-hooks

.PHONY: fmt
fmt:              ## Format code using black & isort.
	pre-commit run --all isort
	pre-commit run --all black

.PHONY: lint
lint:             ## Run pep8, black, mypy linters.
	pre-commit run --all flake8
	pre-commit run --all mypy

.PHONY: test
test:        ## Run tests and generate coverage report.
	pytest -v --cov-config .coveragerc --cov=app  -l --tb=short --cov-fail-under=100  --cov-report term-missing
	coverage xml
	coverage html

.PHONY: run-all-pre-commit-hooks
run-all-pre-commit-hooks:    ## Runs all pre-commit hooks
	pre-commit run --all


.PHONY: clean
clean:            ## Clean unused files.
	@find ./ -name '*.pyc' -exec rm -f {} \;
	@find ./ -name 'Thumbs.db' -exec rm -f {} \;
	@find ./ -name '*~' -exec rm -f {} \;
	@rm -rf .cache
	@rm -rf .pytest_cache
	@rm -rf .mypy_cache
	@rm -rf build
	@rm -rf dist
	@rm -rf *.egg-info
	@rm -rf htmlcov
	@rm -rf .tox/
	@rm -rf docs/_build

.PHONY: check
check: clean run-all-pre-commit-hooks test     ## Runs all checks

.PHONY: virtualenv
virtualenv:       ## Create a virtual environment.
	@if [ "$(USING_POETRY)" ]; then poetry install && exit; fi
	@echo "creating virtualenv ..."
	@rm -rf .venv
	@python3 -m venv .venv
	@./.venv/bin/pip install -U pip
	@echo
	@echo "!!! Please run 'source .venv/bin/activate' to enable the environment !!!"

.PHONY: shell
shell:            ## Open a shell in the project.
	@./.venv/bin/ipython -c "from app import *"
# This makefile copied from https://github.com/rochacbruno/fastapi-project-template/blob/main/Makefile
