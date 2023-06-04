FROM python:3.11-slim-buster

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV APP_HOME=/home/serverless
ENV POETRY_VERSION=1.5.1

RUN mkdir -p $APP_HOME

WORKDIR $APP_HOME

RUN pip install "poetry==$POETRY_VERSION"

COPY pyproject.toml $APP_HOME/


RUN poetry install --without dev

COPY . $APP_HOME/

CMD ["poetry", "run", "python", "main.py"]

