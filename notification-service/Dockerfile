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
CMD /env/bin/uvicorn src.notification_service.asgi:app --reload --host 0.0.0.0 --port 8005