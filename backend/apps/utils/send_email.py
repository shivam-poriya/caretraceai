from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import os


def send_email(to_email: str, subject: str, html_content: str):
    """Generic helper to send HTML emails via SMTP."""
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")

    if not smtp_username or not smtp_password:
        print("[!] SMTP credentials not configured. Skipping email send.")
        return False

    msg = MIMEMultipart()
    msg["From"] = smtp_username
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(html_content, "html"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, to_email, msg.as_string())
        server.quit()
        print(f"[+] Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"[-] Failed to send email to {to_email}: {e}")
        return False


def register_user_send_email(to_email: str, subject: str, html_content: str):
    send_email(to_email, subject, html_content)


def send_otp_email(to_email: str, otp: str):
    """Sends Password Reset OTP via email."""
    subject = "Clinic Intake Assistant — Password Reset OTP"
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; }}
            .container {{ max-width: 500px; margin: auto; background: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
            .header {{ text-align: center; color: #0284c7; border-bottom: 2px solid #e0f2fe; padding-bottom: 15px; }}
            .otp-box {{ background-color: #f0f9ff; border: 2px dashed #0284c7; font-size: 32px; font-weight: bold; letter-spacing: 6px; color: #0369a1; text-align: center; padding: 15px; margin: 25px 0; border-radius: 6px; }}
            .footer {{ margin-top: 30px; font-size: 12px; color: #64748b; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Clinic Intake Assistant</h2>
            </div>
            <p>Hello,</p>
            <p>You requested to reset your password. Use the following 6-digit One-Time Password (OTP) to complete your request:</p>
            <div class="otp-box">{otp}</div>
            <p><strong>Note:</strong> This OTP is valid for <strong>10 minutes</strong>. If you did not request a password reset, please ignore this email.</p>
            <div class="footer">
                <p>Clinic Intake Assistant &copy; 2026. GenAI for Good Project.</p>
            </div>
        </div>
    </body>
    </html>
    """
    send_email(to_email, subject, html_content)
