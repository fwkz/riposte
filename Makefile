RIPOSTE=riposte

define colorecho
      @tput setaf 6
      @echo $1
      @tput sgr0
endef

.PHONY: build
build:
	$(call colorecho, "\nBuilding 'riposte' docker image...")
	docker build -t $(RIPOSTE) .


.PHONY: functional
functional:
	$(call colorecho, "\nRunning functional tests...")
	docker run --rm $(RIPOSTE) tests tests/functional


.PHONY: unit
unit: clean
	$(call colorecho, "\nRunning unit tests...")
	pytest $(ARGS) --ignore tests/functional


.PHONY: lint
lint:
	$(call colorecho, "\nLinting...")
	flake8
	unify --quote \" --check-only --recursive .
	isort --diff

.PHONY: clean
clean:
	$(call colorecho, "\nRemoving artifacts...")
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f  {} +

.PHONY: prune
prune:
	docker ps --filter status=exited -q 2>/dev/null | xargs docker rm -v 2>/dev/null
	docker images --filter dangling=true -q 2>/dev/null | xargs docker rmi 2>/dev/null
	docker network prune -f