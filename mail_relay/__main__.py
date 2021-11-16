"""mail_relay: A simplistic SMTP relay service for Gmail and Home Assistant"""

__email__ = "daniel@engvalls.eu"
__version__ = '0.0.1'

import os
import signal
import httpx
from aiosmtpd.controller import Controller
import asyncio
from loguru import logger
from config import Config
from pathlib import Path
from notifiers import get_notifier
from email.parser import BytesParser


default_config = """
smtp_port: `$SMTP_PORT|9025`
tls_port: `$SMTP_PORT|9587`
gmail: {
    enabled: `$MAIL_FORWARD|false`,
    username: `$MAIL_USERNAME`,
    password: `$MAIL_PASSWORD`
    to: `$MAIL_TO`
}
hass: {
    enabled: `$HASS_ENABLED|false`,
    host: `$HASS_HOST`,
    port: `$HASS_PORT|8123`,
    target: `$HASS_TARGET`,
    key: `$HASS_KEY`
}
"""


def get_config(default_config: str) -> Config:
    """Take default configuration and create file if needed

    :param default_config:
    :return: Config
    """
    if p := os.getenv('CONFIG_PATH', None):
        d = Path(p)
    else:
        d: Path = Path(__file__).parent.absolute() / Path("../config")
    config_fn = d / Path(Path(__file__).parent.stem).with_suffix(".cfg")
    if not config_fn.parent.exists():
        d.mkdir(parents=True, exist_ok=True)
    if not config_fn.exists():
        logger.info("Configuration created")
        config_fn.write_text(default_config)
    return Config(config_fn.as_posix())


class MySmtpHandler:
    def __init__(self, config: Config):
        """Dependency injected for SMTP Controller

        :param config: Required config object for DATA handler
        """
        super().__init__()
        self.config = config

    async def handle_DATA(self, server, session, envelope):
        """Overriden handler for custom behavior after SMTP DATA been supplied

        :param server:
        :param session:
        :param envelope:
        :return:
        """
        logger.debug("Message from %s" % envelope.mail_from)
        logger.debug("Message for %s" % envelope.rcpt_tos)
        logger.debug("Message data:\n")
        subject, message = "", ""
        b = envelope.content
        b = b.decode("utf8", errors="replace") if isinstance(b, bytes) else b
        for ln in b.splitlines():
            print(f"> {ln}".strip())
            if ln.lower().startswith("subject:"):
                _, subject = ln.split(": ", maxsplit=1)
            message += f"{ln}\n"
        logger.debug("End of message")
        await self.sender(subject, message)
        return "250 Message accepted for delivery"

    async def sender(self, subject: str, message: str) -> None:
        """Config object determines which platforms to send to

        :param config: Config object
        :param subject:
        :param message:
        :return:
        """
        config = self.config
        if config["gmail"]["enabled"] in (True, "true"):
            logger.info("email enabled")
            await self.notify_gmail(message, subject)
        if config["hass"]["enabled"] in (True, "true"):
            logger.info("hass enabled")
            h = config["hass"]
            logger.info(f'sending to Home Assistant {h["host"]}')
            try:
                await self.notify_hass(subject, h["host"], h["target"], h["key"])
            except (httpx.NetworkError, httpx.TimeoutException):
                logger.error("failed sending to hass")

    async def notify_gmail(self, message: str, subject: str) -> None:
        """Sends notification with settings from config

        :param config:
        :param message:
        :param subject:
        :return:
        """
        config = self.config
        body = ""
        mail = BytesParser().parsebytes(message.encode())
        if mail.is_multipart():
            parts = [_.get_payload() for _ in mail.get_payload()]
            if parts:
                body = "\n".join(parts)
        else:
            body = message
        logger.info(f"{body=}")
        logger.info("sending gmail")
        g = get_notifier("gmail")
        c = config["gmail"]
        c.pop("enabled")
        await asyncio.to_thread(g.notify, **{"subject": subject, "message": body, **c})

    async def notify_hass(
        self,
        message: str,
        host: str,
        target: str,
        key: str,
        attachment_url: bool = None,
        attachment_content_type: bool = None,
        port: int = 8123,
    ) -> None:
        """Notification to Home Assistant platform

        :param message: Message to be sent
        :param host: HASS host
        :param target: Being the notification "target" define within Home Assistant
        :param key: The API key
        :param attachment_url: If a attachment to be sent along
        :param attachment_content_type:  Content type required for attachment
        :param port: HASS port
        :return:
        """
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        payload = {
            "message": message,
        }
        if all((attachment_url, attachment_content_type)):
            payload["data"] = {
                "attachment": {
                    "url": attachment_url,
                    "hide-thumbnail": False,
                }
            }
        async with httpx.AsyncClient() as x:
            r = await x.post(
                f"http://{host}:{port}/api/services/notify/{target}",
                headers=headers,
                json=payload,
            )
            logger.debug(f"hass response: {r}")


def main():
    c = get_config(default_config)
    controller_plain = Controller(
        MySmtpHandler(c), hostname="0.0.0.0", port=c["smtp_port"]
    )
    controller_tls = Controller(
        MySmtpHandler(c), decode_data=True, hostname="0.0.0.0", port=c["tls_port"]
    )
    o = (controller_plain, controller_tls)
    for client in o:
        client.start()
    logger.info(f"SMTP relay been started")
    logger.info(f"listening to ports {c['smtp_port']}(SMTP) {c['tls_port']}(TLS)")
    logger.info("CTRL-C to exit")
    signal.pause()
    for client in o:
        client.stop()


if __name__ == "__main__":
    main()
