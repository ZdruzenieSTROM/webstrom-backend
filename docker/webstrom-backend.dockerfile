FROM python:3.13

WORKDIR /app

COPY Pipfile /app
COPY Pipfile.lock /app

RUN pip install pipenv
RUN pipenv sync --dev --system

COPY . /app

CMD [ "gunicorn", "-b", "0.0.0.0", "-p", "8000", "webstrom.wsgi:application" ]
