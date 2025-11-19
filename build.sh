#!/usr/bin/env bash
# exit on error
set -o errexit

echo "==> Installing dependencies..."
pip install -r requirements.txt

echo "==> Checking static directory..."
ls -la static/ || echo "static directory not found"

echo "==> Creating staticfiles directory..."
mkdir -p staticfiles

echo "==> Collecting static files..."
python manage.py collectstatic --no-input --clear --verbosity 2

echo "==> Verifying staticfiles were collected..."
if [ -d "staticfiles" ]; then
    echo "staticfiles directory exists"
    ls -la staticfiles/
    if [ -d "staticfiles/img" ]; then
        echo "img directory found in staticfiles"
        ls -la staticfiles/img/
    else
        echo "WARNING: img directory NOT found in staticfiles"
    fi
else
    echo "ERROR: staticfiles directory was not created"
fi

echo "==> Running migrations..."
python manage.py migrate

echo "==> Build completed successfully!"
