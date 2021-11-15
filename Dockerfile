FROM python:3.8-slim-buster

WORKDIR /app
RUN mkdir config
COPY . .
RUN python setup.py install
CMD ['mail_relay']