######################
## PATHS DEFINITION ##
######################
persistent_path := local.persistent
local_virtualenv_path := local.virtualenv

install-virtualenv: clean
	./install-virtualenv.sh

requirements:
	./install-virtualenv.sh requirements.txt
	#./scripts/local/freeze-requirements.sh

run-all: run

######################
## TESTS AND CHECKS ##
######################

test:
	./local.virtualenv/bin/pytest $(args)

run:
	./run.sh
