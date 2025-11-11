
import os, aiosmtplib
from email.message import EmailMessage

SMTP_HOST = os.getenv("SMTP_HOST","localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT","1025"))
FROM_ADDR = os.getenv("FROM_ADDR","noreply@campus.local")

async def send_mail(to:str, subject:str, body:str):
    msg = EmailMessage()
    msg["From"] = FROM_ADDR
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    await aiosmtplib.send(msg, hostname=SMTP_HOST, port=SMTP_PORT, start_tls=False)
