rm db.sqlite3
python manage.py makemigrations document
python manage.py sqlmigrate document 0001
python manage.py migrate
rm -rf /tmp/u2