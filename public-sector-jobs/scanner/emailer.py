"""Send the report over SMTP (defaults to Gmail with an app password)."""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send(subject, html, to_addr):
    host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    port = int(os.environ.get("SMTP_PORT", "587"))
    user, pw = os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"]
    msg = MIMEMultipart("alternative")
    msg["Subject"], msg["From"], msg["To"] = subject, os.environ.get("SMTP_FROM", user), to_addr
    msg.attach(MIMEText("This report is HTML - please view it in an HTML-capable mail client.", "plain"))
    msg.attach(MIMEText(html, "html", "utf-8"))
    with smtplib.SMTP(host, port) as s:
        s.starttls()
        s.login(user, pw)
        s.sendmail(msg["From"], [a.strip() for a in to_addr.split(",")], msg.as_string())
