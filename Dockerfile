FROM python:3.9-slim-buster

EXPOSE 9025
EXPOSE 9587

RUN apt-get -y update
RUN apt-get -y install git

WORKDIR /app
RUN mkdir config
RUN pip3 install git+https://github.com/engdan77/mail_relay.git
CMD ["mail_relay"]