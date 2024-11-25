FROM public.ecr.aws/docker/library/python:3.12 as base

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1
ENV POETRY_VIRTUALENVS_CREATE=false
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends gcc
RUN pip install --upgrade pip && pip install --no-cache-dir poetry

WORKDIR /code
COPY pyproject.toml poetry.lock /code/

RUN poetry install --no-ansi --no-interaction

COPY . /code

# this is only setup in dev env, not prod Dockerfile
ENTRYPOINT ["/code/docker-entrypoint.sh"]

EXPOSE 8000
