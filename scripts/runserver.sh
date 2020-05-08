#!/bin/bash
export $(cat .env_dev_local | xargs) && python manage.py runserver