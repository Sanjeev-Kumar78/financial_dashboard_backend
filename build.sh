#!/bin/bash
# Vercel build script - applies Alembic migrations

set -e

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running database migrations..."
alembic upgrade head

echo "Build complete!"
