######################
## PATHS DEFINITION ##
######################
persistent_path := local.persistent
virtualenv_path := local.virtualenv

install-virtualenv:
	./install-virtualenv.sh

requirements:
	./install-virtualenv.sh requirements.txt

settings:
	$(virtualenv_path)/bin/ansible-playbook scripts/ansible/playbook.yml --inventory scripts/ansible/local.yml --diff

settings-docker:
	$(virtualenv_path)/bin/ansible-playbook scripts/ansible/playbook.yml --inventory scripts/ansible/deploy.yml --diff

settings-docker-local:
	$(virtualenv_path)/bin/ansible-playbook scripts/ansible/playbook.yml --inventory scripts/ansible/docker-local.yml --diff

install-persistent:
	mkdir -p $(persistent_path)
	mkdir -p $(persistent_path)/event
	touch $(persistent_path)/event/event_store.db

create-local-database:
	python ./scripts/create_database.py

install: requirements install-persistent settings create-local-database

install-docker: requirements install-persistent settings-docker create-local-database

install-docker-local: requirements install-persistent settings-docker-local create-local-database

run-all: run

coverage:
	./scripts/coverage.sh

######################
## TESTS AND CHECKS ##
######################

test: linter
	./local.virtualenv/bin/pytest $(args)

run:
	./run.sh

linter:
	flake8 --verbose --ignore E501 --exclude $(virtualenv_path)
