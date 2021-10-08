.PHONY: install
install:
	pip install --upgrade pip setuptools wheel
	pip install -r requirements.txt

.PHONY: install-dev
install-dev: install
	pip install -r requirements-dev.txt
	python setup.py develop

.PHONY: lint
lint:
	flake8 chaosk8s/ tests/
	isort --check-only --profile black chaosk8s/ tests/
	black --check --diff chaosk8s/ tests/

.PHONY: format
format:
	isort --profile black chaosk8s/ tests/
	black chaosk8s/ tests/

.PHONY: tests
tests:
	pytest
