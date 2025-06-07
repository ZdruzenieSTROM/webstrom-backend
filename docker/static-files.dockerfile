FROM python:3.13 AS static-files-builder

WORKDIR /app

COPY Pipfile /app
COPY Pipfile.lock /app

RUN pip install pipenv
RUN pipenv sync --dev --system

COPY . /app

RUN python manage.py collectstatic --no-input

FROM nginx:1.28

COPY --from=static-files-builder /app/static /usr/share/nginx/html
