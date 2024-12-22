#!/bin/bash

# Exit script if any command fails
set -e

echo "Starting deployment process..."

# Paths
PROJECT_DIR="/home/ubuntu/iaapp" # Adjust this to the path of your project
VENV_DIR="$PROJECT_DIR/venv"

# Move to the project directory
echo "Navigating to the project directory..."
cd $PROJECT_DIR

# Update the Git repository
echo "Pulling latest changes from Git..."
git pull origin main

# Activate the virtual environment
echo "Activating the Python virtual environment..."
source $VENV_DIR/bin/activate

# Install Python dependencies
echo "Installing Python dependencies from requirements.txt..."
pip install -r requirements.txt

# Build frontend assets using Node.js
echo "Building frontend assets with Node.js..."
npm install
npm run build

# Collect static files for Django
echo "Collecting Django static files..."
python manage.py collectstatic --noinput

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Restart the Gunicorn service
echo "Restarting Gunicorn service..."
sudo systemctl restart gunicorn

# Restart Nginx (optional, usually not necessary if only app changes are made)
echo "Restarting Nginx service..."
sudo systemctl restart nginx

echo "Deployment completed successfully!"
