FROM python:3.6

RUN pip install -U pip

WORKDIR /riposte

COPY . .

RUN pip install .[dev]

ENTRYPOINT ["/riposte/docker-entrypoint.sh"]