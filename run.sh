#!/bin/bash

uvicorn main:app --host 0.0.0.0 --port 8081 --reload --reload-dir command --reload-dir domain --reload-dir infrastructure --reload-dir web --log-config log-config.json