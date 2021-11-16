[![Docker](https://badgen.net/badge/icon/docker?icon=docker&label)](https://https://docker.com/)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-360/)

## Mail Relay

### Background

While integrating the lawn mower to my existing home automation this embedded platform were only able to use plain [SMTP](https://datatracker.ietf.org/doc/html/rfc5321) for sending notification in comparison authenticating and trasmitting across TLS ([rfc3207](https://datatracker.ietf.org/doc/html/rfc3207)) that made it troublesome without a way for me "relaying" e-mail through another service. Now another advantage that came to my mind using this allows "all" my internal services (platforms) to be configured to be used one single "mail" service that allows me to reconfigure for any new mail destination without need doing this across all services.

I also extended this package also adding possibility to send notification to a [Home Assistant](https://www.home-assistant.io) environment e.g. allowing "push" messages to Apple IOS or Android devices.

### Installation
#### From source
````shell
pip3 install git+https://github.com/engdan77/mail_relay.git
````
#### From Dockerhub
```shell
mkdir config
docker run -p 9587:9587 -p 9025:9025 -v $(pwd)/config:/app/config -e CONFIG_PATH='/app/config' --name mail_relay engdan77/mail_relay
```

First run if no mail_relay.cfg been created a default one will be created that could be updated.

### Example configuration

This is a sample *mail_relay.cfg* where a default one being automatically generated within the config folder.

```properties

smtp_port: `$SMTP_PORT|9025`
tls_port: `$SMTP_PORT|9587`
gmail: {
    enabled: true,
    username: 'mygmailaccount',
    password: 'mypassword',
    to: 'myemail@foo.com'
}
hass: {
    enabled: true,
    host: `$HASS_HOST`,
    port: `$HASS_PORT`,
    target: `$HASS_TARGET`,
    key: `$HASS_KEY`
}

```

Now the $XXX|YYY means that if an environment variable XXX exists it will be used otherwise use YYY. More information can be read [here](https://docs.red-dove.com/cfg/python.html).

### Configure gmail service

All you need to supply is your gmail username, password and the email you like message to be forwarded to.

### Configure "notification" service in Home Assistant

If you look closer how to add "[notification](https://www.home-assistant.io/integrations/notify/)" in HASS to be used as <u>key</u> in above configuration. And you also need to get access token (key) to be used with your integration, more information [here](https://www.home-assistant.io/docs/authentication/ ).

A Home Assistant *configuration.yaml* where in such example I could use <u>all_iphones</u> set as target in above mail_relay configuration.

```yaml
notify:
  - name: all_iphones
    platform: group
    services:
      - service: mobile_app_my_iphone
      - service: mobile_app_other_iphone
```

### Tests and coverage

```text
pytest --cov
================ test session starts =========================
platform darwin -- Python 3.9.5, pytest-6.2.5, py-1.10.0, pluggy-1.0.0
rootdir: /Users/edo/git/my/mail_relay
plugins: anyio-3.3.1, mock-3.6.1, cov-3.0.0, httpx-0.13.0
collected 4 items                                                                                                                                                          

tests/test_mail_relay.py ....                                                                                                                                        [100%]

---------- coverage: platform darwin, python 3.9.5-final-0 -----------
Name                     Stmts   Miss  Cover
--------------------------------------------
mail_relay/__init__.py       1      0   100%
mail_relay/__main__.py      91     21    77%
--------------------------------------------
TOTAL                       92     21    77%
```