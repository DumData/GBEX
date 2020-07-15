#!/bin/bash
export $(cat .env | xargs) && vepy/bin/python manage.py makemigrations && vepy/bin/python manage.py migrate && echo \"from scripts import init_scripts\" | vepy/bin/python manage.py shell && vepy/bin/python manage.py createinitialrevisions && vepy/bin/python manage.py collectstatic
