#!/bin/bash
# scripts/start-backend.sh
cd backend
poetry run uvicorn app.infrastructure.api.main:app --reload --host 127.0.0.1 --port 8000