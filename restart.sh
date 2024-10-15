sh sivacenv/bin/activate
python manage.py collectstatic
sudo systemctl restart gunicorn
sudo systemctl restart nginx
