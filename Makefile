######################
## PATHS DEFINITION ##
######################
persistent_path := local.persistent
virtualenv_path := .venv

install-virtualenv:
	@poetry config virtualenvs.in-project true
	@poetry config virtualenvs.path .venv
	@poetry install $(INSTALL_ARGS)

settings:
	$(virtualenv_path)/bin/ansible-playbook scripts/ansible/playbook.yml --inventory scripts/ansible/local.yml --diff

settings-docker:
	$(virtualenv_path)/bin/ansible-playbook scripts/ansible/playbook.yml --inventory scripts/ansible/deploy.yml --diff -vvvv

settings-docker-local:
	$(virtualenv_path)/bin/ansible-playbook scripts/ansible/playbook.yml --inventory scripts/ansible/docker-local.yml --diff

install-persistent:
	mkdir -p $(persistent_path)
	mkdir -p $(persistent_path)/event
	touch $(persistent_path)/event/event_store.db

create-local-database:
	python ./scripts/create_database.py

install: install-virtualenv install-persistent settings create-local-database

install-docker: install-virtualenv install-persistent settings-docker create-local-database

install-docker-local: install-virtualenv install-persistent settings-docker-local create-local-database

run-all: run

coverage:
	./scripts/coverage.sh

######################
## TESTS AND CHECKS ##
######################

test: linter
	./.venv/bin/pytest $(args)

run:
	./run.sh

linter:
	flake8 --verbose --ignore E501 --exclude $(virtualenv_path)
