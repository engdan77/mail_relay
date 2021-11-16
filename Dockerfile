FROM python:3.8-slim-buster

WORKDIR /app
RUN mkdir config
RUN pip3 install git+https://github.com/engdan77/mail_relay.git
CMD ["mail_relay"]