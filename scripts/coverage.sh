#!/bin/bash

PATH=./local.virtualenv/bin:$PATH
COVARGS="\
    --cov-report=html \
    --cov=command \
    --cov=domain \
    --cov=event \
    --cov=infrastructure \
    --cov=web \
"

pytest "$*" $COVARGS
