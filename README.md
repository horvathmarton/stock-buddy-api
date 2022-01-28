# Stock buddy api

## dev notes
getting started:
- start postgresql eihter as a service or container (docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=mysecretpassword  postgres)
- install recent 3.9=< version python and pip
- install postgresql-dev for the binary dependencies 
- pip install -r requirements.txt
- (destructive) python manage.py recreate_db
- (destructive) python manage.py migrate
- start it with: python manage.py runserver 

or by starting `docker-compose build && docker-compose up`
