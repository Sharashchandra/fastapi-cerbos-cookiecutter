#!/bin/sh

# stop the script if any command fails
set -e

# Run Alembic migrations
alembic upgrade head

# Execute the passed command (CMD from Dockerfile or command from docker-compose.yml)
exec "$@"
