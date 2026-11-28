FROM python:3.13

WORKDIR /app

COPY Pipfile /app
COPY Pipfile.lock /app

RUN pip install pipenv
RUN pipenv sync --dev --system

COPY . /app

# Gunicorn's own default is a single sync worker, so one slow request blocks every other.
# Each worker holds ~130 MB; the host has 2 CPUs and runs both prod and test.
ENV WEB_CONCURRENCY=3

# Use PORT env var for host networking
CMD sh -c "gunicorn -b 0.0.0.0:${PORT:-8000} webstrom.wsgi:application"
