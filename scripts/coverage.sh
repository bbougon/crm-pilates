#!/bin/bash

PATH=./.venv/bin:$PATH
COVARGS="\
    --cov-report=html \
    --cov=crm_pilates/command \
    --cov=crm_pilates/domain \
    --cov=crm_pilates/event \
    --cov=crm_pilates/infrastructure \
    --cov=crm_pilates/web \
"

pytest "$*" $COVARGS
