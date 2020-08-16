FROM python:3.7 as base

FROM base as builder
RUN pip3 install poetry==1.0.3
COPY . /src/
WORKDIR /src
RUN python3 -m venv /env && . /env/bin/activate && poetry install

FROM base
COPY --from=builder /env /env
COPY --from=builder /src /src
WORKDIR /src
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait
CMD /wait alembic upgrade head & /env/bin/uvicorn src.notification_service.asgi:app --reload --host 0.0.0.0 --port 8005