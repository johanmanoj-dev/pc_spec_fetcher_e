import smtplib
import socket
import os
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


def send_report(report_path: str, config: dict) -> bool:
    """
    Send the diagnostics report via SMTP.

    config keys:
        smtp_host     — e.g. "smtp.gmail.com"
        smtp_port     — e.g. 587
        sender_email  — your Gmail address
        app_password  — Gmail App Password (not your real password)
        recipient     — where to send the report
    """
    load_dotenv()
    sender = config.get("sender_email") or os.getenv("SENDER_EMAIL")
    recipient = config.get("recipient") or os.getenv("RECIPIENT_EMAIL")
    subject = f"PC Diagnostics Report — {config.get('hostname') or os.getenv('HOSTNAME', 'Unknown PC')}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    # Plain text body
    body_text = (
        "Hello,\n\n"
        "Your PC diagnostics report has been generated automatically.\n"
        "Please find the full HTML report attached.\n\n"
        "— PC Diagnostics Tool"
    )
    msg.attach(MIMEText(body_text, "plain"))

    # Attach the HTML report file
    if os.path.exists(report_path):
        with open(report_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        filename = os.path.basename(report_path)
        part.add_header("Content-Disposition", f"attachment; filename={filename}")
        msg.attach(part)

    # Connect and send
    try:
        host = config.get("smtp_host") or os.getenv("SMTP_HOST", "smtp.gmail.com")
        port = config.get("smtp_port") or os.getenv("SMTP_PORT", "587")
        password = config.get("app_password") or os.getenv("APP_PASSWORD")

        with smtplib.SMTP(host, int(port), timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
    except smtplib.SMTPAuthenticationError:
        raise RuntimeError(
            "Authentication failed. Check your sender email and app password in Settings."
        )
    except (socket.gaierror, OSError):
        raise RuntimeError(
            "Could not connect to the mail server. Check your internet connection and SMTP host/port."
        )
    except smtplib.SMTPException as e:
        raise RuntimeError(f"Email sending failed: {e}")

    return True