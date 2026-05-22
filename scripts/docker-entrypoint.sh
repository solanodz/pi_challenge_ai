#!/bin/sh
set -e

if [ "${SKIP_INGEST:-false}" != "true" ]; then
  echo "Running corpus ingest..."
  python scripts/ingest.py
else
  echo "Skipping ingest (SKIP_INGEST=true)."
fi

echo "Starting API on port 8000..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000
