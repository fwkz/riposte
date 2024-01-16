REFORMAT_DIRS:=riposte

define colorecho
      @tput setaf 6
      @echo $1
      @tput sgr0
endef


.PHONY: all
all: reformat tests lint


.PHONY: package
package: clean
	$(call colorecho, "\n Building package distributions...")
	python -m build .


.PHONY: publish
publish: package
	twine upload dist/*


.PHONY: tests
tests: clean
	$(call colorecho, "\nRunning tests...")
	pytest $(ARGS)


.PHONY: lint
lint:
	$(call colorecho, "\nLinting...")
	black --check --diff $(REFORMAT_DIRS)
	isort --check-only --diff $(REFORMAT_DIRS)
	ruff check --diff $(REFORMAT_DIRS)

.PHONY: reformat
reformat:
	$(call colorecho, "\nReformatting...")
	black $(REFORMAT_DIRS)
	isort $(REFORMAT_DIRS)
	ruff check --fix $(REFORMAT_DIRS)

.PHONY: clean
clean:
	$(call colorecho, "\nRemoving artifacts...")
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f  {} +
	rm -rf build dist pip-wheel-metadata