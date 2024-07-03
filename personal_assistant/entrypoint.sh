#!/bin/bash
set -e

# Run database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Execute the command passed to the entrypoint
exec "$@"
