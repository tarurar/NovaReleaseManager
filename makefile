.PHONY: typehint
typehint:
	mypy .

.PHONY: test
test:
	pytest

.PHONY: lint
lint:
	pylint **/*.py --rcfile=.pylintrc

.PHONY: checklist
checklist: lint typehint test

.PHONY: format
black:
	black -l 80 *.py

.PHONY: clean
clean:
	find . -type f -name '*.pyc' | xargs rm -fr
	find . -type d -name '__pycache__' | xargs rm -fr