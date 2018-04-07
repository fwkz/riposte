.PHONY: test
test:
	pytest $(ARGS)

.PHONY: lint
lint:
	flake8
	unify --quote \" --check-only --recursive .
	isort --diff