#!/bin/bash
export $(cat .env_not_docker | xargs) && python manage.py createsuperuser
