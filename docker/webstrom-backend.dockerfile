FROM python:3.13

WORKDIR /app

COPY Pipfile /app
COPY Pipfile.lock /app

RUN pip install pipenv
RUN pipenv sync --dev --system

COPY . /app

# Use PORT env var for host networking
CMD sh -c "gunicorn -b 0.0.0.0:${PORT:-8000} webstrom.wsgi:application"
