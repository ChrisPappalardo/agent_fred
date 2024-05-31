.PHONY: all clean clean-build clean-pyc clean-test docs docs_build docs_clean docs_linkcheck api_docs_build api_docs_clean api_docs_linkcheck format lint pre-commit test tests test_watch integration_tests docker_tests help extended_tests

# Default target executed when no arguments are given to make.
all: help

# remove all build, test, coverage and Python artifacts
clean: clean-build clean-pyc clean-test

# remove build artifacts
clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

# remove Python file artifacts
clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

# remove test, lint, typing, and coverage artifacts
clean-test:
	rm -f .coverage
	rm -fr .mypy_cache
	rm -fr .pytest_cache
	rm -fr .ruff_cache

######################
# TESTING AND COVERAGE
######################

# Run unit tests and generate a coverage report.
coverage:
	DEBUG=True poetry run pytest --cov \
		--cov-config=.coveragerc \
		--cov-report xml \
		--cov-report term-missing:skip-covered

# Define a variable for the test file path.
TEST_FILE ?= tests/

test:
	DEBUG=True poetry run pytest $(TEST_FILE)

tests:
	DEBUG=True poetry run pytest $(TEST_FILE)

extended_tests:
	DEBUG=True poetry run pytest --only-extended tests/unit_tests

test_watch:
	DEBUG=True poetry run ptw --now . -- tests/unit_tests

# integration_tests:
# 	poetry run pytest tests/integration_tests

# docker_tests:
# 	docker build -t my-langchain-image:test .
# 	docker run --rm my-langchain-image:test

########################
# LINTING AND FORMATTING
########################

# Define a variable for Python and notebook files.
PYTHON_FILES=.
lint format: PYTHON_FILES=.
lint_diff format_diff: PYTHON_FILES=$(shell git diff --relative=libs/langchain --name-only --diff-filter=d master | grep -E '\.py$$|\.ipynb$$')

lint lint_diff:
	poetry run mypy $(PYTHON_FILES)
	poetry run black $(PYTHON_FILES) --check
	poetry run ruff .

format format_diff:
	poetry run black $(PYTHON_FILES)
	poetry run ruff --select I --fix $(PYTHON_FILES)

pre-commit:
	poetry run pre-commit run --all-files

spell_check:
	poetry run codespell --toml pyproject.toml

spell_fix:
	poetry run codespell --toml pyproject.toml -w


###############
# DOCUMENTATION
###############

docs docs_build:
	poetry run mkdocs build


######
# HELP
######

help:
	@echo '===================='
	@echo 'clean                        - run clean-build clean-pyc clean-test'
	@echo '-- DOCUMENTATION --'
	@echo 'docs_build                   - build the documentation'
	@echo '-- LINTING --'
	@echo 'format                       - run code formatters'
	@echo 'lint                         - run linters'
	@echo 'pre-commit                   - run pre-commit pipeline'
	@echo 'spell_check                  - run codespell on the project'
	@echo 'spell_fix                    - run codespell on the project and fix the errors'
	@echo '-- TESTS --'
	@echo 'coverage                     - run unit tests and generate coverage report'
	@echo 'test                         - run unit tests'
	@echo 'tests                        - run unit tests (alias for "make test")'
	@echo 'test TEST_FILE=<test_file>   - run all tests in file'
	@echo 'extended_tests               - run only extended unit tests'
	@echo 'test_watch                   - run unit tests in watch mode'
	@echo 'integration_tests            - run integration tests'
	@echo 'docker_tests                 - run unit tests in docker'
