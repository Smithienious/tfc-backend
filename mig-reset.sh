find . -type f -name "*.py[co]" -delete
find . -type d -name "__pycache__" -delete
find . -depth -type d -name ".mypy_cache" -exec rm -r {} +
find . -depth -type d -name ".pytest_cache" -exec rm -r {} +
find . -path "*/migrations/*.py" -not -name "__init__.py" -not -path "*/db/*" -delete

python manage.py makemigrations
python manage.py migrate
