sh sivacenv/bin/activate
python3 ./manage.py dumpdata --exclude auth.permission --exclude contenttypes > ../db.json
tar cfvj ../backup-sivac.tar.bz2 media ../db.json
