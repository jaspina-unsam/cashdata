#!/bin/bash
# scripts/start-backend.sh
cd backend
poetry run uvicorn cashdata.infrastructure.api.main:app --reload --host 0.0.0.0 --port 8000