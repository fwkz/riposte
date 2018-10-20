define colorecho
      @tput setaf 6
      @echo $1
      @tput sgr0
endef


.PHONY: all
all: reformat unit lint


.PHONY: unit
unit: clean
	$(call colorecho, "\nRunning unit tests...")
	pytest $(ARGS)


.PHONY: lint
lint:
	$(call colorecho, "\nLinting...")
	flake8
	black --check --diff .
	isort --check-only --diff


.PHONY: reformat
reformat:
	$(call colorecho, "\nReformatting...")
	black .
	isort -y


.PHONY: clean
clean:
	$(call colorecho, "\nRemoving artifacts...")
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f  {} +