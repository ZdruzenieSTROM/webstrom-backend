#!/bin/bash

python manage.py restoredb

daphne -b 0.0.0.0 -p 8000 webstrom.asgi:application
