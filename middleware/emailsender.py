import ssl
from datetime import datetime as dt
from decouple import config
from smtplib import SMTP_SSL

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

HOST = config("SMTP_HOST")
PORT = config("SMTP_PORT", default=465, cast=int)
SENDER = config("SMTP_SENDER")
PASSWORD = config("SMTP_PASSWORD")
RECEIVER = config("EMAIL_RECEIVER")

print(config("SMTP_PASSWORD"))


def send(image: bytes):
    subject = "Detection Alert 🚨"
    body = f"{dt.now():%Y-%m-%d at %H:%M}"

    msg = MIMEMultipart()
    msg["From"] = f"RPI-CCTV <{SENDER}>"
    msg["To"] = RECEIVER
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    attachment = MIMEImage(image)
    msg.attach(attachment)

    text = msg.as_string()
    ctx = ssl.create_default_context()
    smtp = SMTP_SSL(HOST, PORT, context=ctx)
    with smtp as server:
        server.login(SENDER, PASSWORD)
        server.sendmail(SENDER, RECEIVER, text)
