.PHONY: install dev test format cov-test pre-commit-check

install:
	pip install -e .

dev:
	pip install -e ".[test]"

test:
	python -m pytest ./tests

format:
	pre-commit run --all-files

cov-test:
	python -m pytest ./tests --doctest-modules --junitxml=junit/test-results.xml --cov=jailbreakeval --cov-report=xml --cov-report=html
	
pre-commit-check: format test
