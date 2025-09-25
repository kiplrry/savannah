#!/bin/sh

set -e

echo "📦 Applying database migrations..."
python manage.py migrate --noinput

echo "👤 Ensuring superuser exists..."
python manage.py ensure_superuser

echo "🚀 Starting server..."
exec "$@"
