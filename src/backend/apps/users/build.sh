set -o errexit  # Enable strict error checking

pip install -r ../../../../requirements.txt  # Install the required Python packages

python manage.py collectstatic --no-input  # Collect static files for deployment

python manage.py makemigrations  # Create database migration files
python manage.py migrate  # Apply database migrations
