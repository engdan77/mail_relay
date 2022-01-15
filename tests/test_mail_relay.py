import json
import pytest
from mail_relay import default_config, get_config, MySmtpHandler
from aiosmtpd.controller import Controller
from unittest.mock import patch, Mock
from smtplib import SMTP
from loguru import logger
from pytest_httpx import HTTPXMock


@pytest.fixture
def my_config():
    return {"smtp_port": 9025, "gmail": {"enabled": False}, "hass": {"enabled": False}}


@pytest.fixture
def my_smtp_handler(my_config):
    async def sender(*args):
        return Mock()

    controller = Controller(
        MySmtpHandler(my_config), hostname="127.0.0.1", port=my_config["smtp_port"]
    )
    controller.sender = sender
    controller.start()
    yield controller
    controller.stop()


def send_test_email(hostname, port):
    with SMTP(hostname, port) as client:
        from_addr = "foo@example.org"
        to_addrs = "bar@example.org"
        msg = (
            f"From: {from_addr}\r\n"
            f"To: {to_addrs}\r\n"
            f"Subject: Foo\r\n\r\n"
            f"Foo bar"
        )
        client.set_debuglevel(True)
        client.sendmail(from_addr, to_addrs, msg)
    logger.info("email sent")


def test_get_config(tmp_path):
    tmp_file_path = tmp_path / f"{__name__}.cfg"
    with patch("mail_relay.__main__.Path", return_value=tmp_file_path) as mocked_path:
        config = get_config(default_config)
    mocked_path.assert_called()
    assert set(config.as_dict().keys()) == {
        "smtp_port",
        "gmail",
        "tls_port",
        "hass",
        "api_port"
    }


def test_handle_data(my_smtp_handler, capsys):
    send_test_email("127.0.0.1", 9025)
    assert "250 Message accepted for delivery" in capsys.readouterr().err


@patch("mail_relay.__main__.get_notifier")
def test_notify_gmail(mocked_get_notifier: Mock, my_smtp_handler):
    my_smtp_handler.handler.config["gmail"]["enabled"] = True
    send_test_email("127.0.0.1", 9025)
    mocked_get_notifier.assert_called_with("gmail")


def test_notify_hass(my_smtp_handler, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=200)
    my_smtp_handler.handler.config["hass"] = {
        "enabled": True,
        "host": "host",
        "target": "target",
        "key": "key",
    }
    send_test_email("127.0.0.1", 9025)
    assert json.loads(httpx_mock.get_request().read())["message"] == "Foo"
