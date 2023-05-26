FROM python:3.11

EXPOSE 8000

WORKDIR /app

COPY Pipfile /app
COPY Pipfile.lock /app

RUN ["pip", "install", "pipenv"]
RUN ["pipenv", "install", "--dev", "--deploy", "--system"]

COPY . /app

CMD ["/app/docker_entrypoint.sh"]
