FROM python:3.10-slim

ARG DATABASE_URL
ARG SECRET_KEY

ENV DATABASE_URL=${DATABASE_URL} \
    SECRET_KEY=${SECRET_KEY} \
    ALGORITHM=HS256 \
    ACCESS_TOKEN_EXPIRE_MINUTES=60 \
    APP_ROOT=/server \
    PORT=80

WORKDIR ${APP_ROOT}

COPY requirements.txt ./

RUN pip3 install -r requirements.txt

COPY . ./

EXPOSE 80

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}