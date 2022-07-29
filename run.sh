#!/bin/bash

uvicorn crm_pilates.main:app --host 0.0.0.0 --port 8081 --reload --reload-dir crm_pilates/command --reload-dir crm_pilates/domain --reload-dir crm_pilates/infrastructure --reload-dir crm_pilates/web
