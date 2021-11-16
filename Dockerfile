FROM python:3.8-slim-buster

EXPOSE 9025
EXPOSE 9587

ENV CONFIG_PATH=/app/config

RUN apt-get -y update
RUN apt-get -y install git

WORKDIR /app
RUN mkdir config
RUN pip3 install git+https://github.com/engdan77/mail_relay.git
CMD ["mail_relay"]