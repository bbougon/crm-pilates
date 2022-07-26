#!/bin/sh

gunicorn --config /crm-pilates/crm_pilates/gunicorn.py

echo "exited $0"