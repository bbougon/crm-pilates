######################
## PATHS DEFINITION ##
######################
persistent_path := local.persistent
local_virtualenv_path := local.virtualenv

install-virtualenv:
	./install-virtualenv.sh

requirements:
	./install-virtualenv.sh requirements.txt

run-all: run

######################
## TESTS AND CHECKS ##
######################

tests:
	./local.virtualenv/bin/pytest $(args)

run:
	./run.sh

linter:
	flake8 main.py
