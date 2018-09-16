.PHONY: all
all: lint test

.PHONY: lint
lint:
	isort -y
	unify --quote \" --in-place --recursive .

.PHONY: test
test:
	py.test tests/