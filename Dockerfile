FROM python:3.11

WORKDIR /app

COPY Pipfile /app
COPY Pipfile.lock /app

RUN pip install pipenv
RUN pipenv sync --dev --system

COPY . /app

RUN python manage.py restoredb

EXPOSE 8000

ENTRYPOINT [ "daphne", "-b", "0.0.0.0", "-p", "8000", "webstrom.asgi:application" ]
