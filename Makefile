######################
## PATHS DEFINITION ##
######################
persistent_path := local.persistent
local_virtualenv_path := local.virtualenv

install-virtualenv:
	./install-virtualenv.sh

requirements:
	./install-virtualenv.sh requirements.txt

settings:
	$(local_virtualenv_path)/bin/ansible-playbook scripts/ansible/playbook_settings.yml --inventory scripts/ansible/local.yml --diff --extra-vars "settings_destination={{ repository_path }}"

install-persistent:
	mkdir -p $(persistent_path)
	mkdir -p $(persistent_path)/event
	touch $(persistent_path)/event/event_store.db

create-local-database:
	python ./scripts/create_database.py

install: requirements install-persistent create-local-database

run-all: run

coverage:
	./scripts/coverage.sh

######################
## TESTS AND CHECKS ##
######################

test:
	./local.virtualenv/bin/pytest $(args)

run:
	./run.sh

linter:
	flake8 tests
