"""
Password Reset Email Sender Module

This module is responsible for sending **password reset verification emails**
for the Campus E-Wallet System using Gmail’s SMTP service.

Main Responsibilities:
- Compose and send password reset emails in both **plain text** and **HTML**
- Deliver a time-sensitive verification code to the user’s registered email
- Provide a clean, user-friendly HTML email layout
- Use secure SSL-based SMTP communication

Email Features:
- Clear password reset instructions
- Prominently displayed verification code
- Expiration notice (5 minutes)
- Fallback plain-text version for email clients that do not support HTML

Security Notes:
- Uses SSL encryption for SMTP communication
- Requires an app-specific Gmail password (recommended)
- No verification logic is handled here (email sending only)

Dependencies:
- smtplib and ssl for secure email transport
- email.mime for constructing multipart email messages

This module is intended to be called by authentication or password recovery
services (e.g., LoginSystem) when a user requests a password reset.
"""

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_password_reset_email(recipient_email, reset_code):
    """
    Send a password reset verification email to a student.

    Parameters:
        recipient_email (str): The student's registered email address.
        reset_code (str): The one-time verification code for resetting the password.

    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    # Sender credentials
    sender_email = "campus.ewallet@gmail.com"
    sender_password = "temporary password to protect the account"  

    # Email subject
    subject = "Campus E-Wallet System - Password Reset Verification"

    # Plain text version of the email (for clients that do not support HTML)
    plain_text = (
        f"Hello user,\n\n"
        f"You requested to reset your Campus E-Wallet password.\n\n"
        f"Use the verification code below to reset your password:\n\n"
        f"Reset Code: {reset_code}\n\n"
        f"This code is valid for 5 minutes.\n"
        f"If you did not request a password reset, please ignore this email.\n\n"
        f"Campus E-Wallet System Team"
    )

    # HTML version of the email with styling and prominent code display
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 30px;">
        <div style="max-width: 480px; margin: auto; background: white; padding: 25px; border-radius: 10px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);">

            <h2 style="color: #27ae60; text-align: center; margin-top: 10px;">
                Campus E-Wallet Password Reset
            </h2>

            <p>Hello user,</p>

            <p>
                You requested to reset your password. Please use the verification code below to proceed:
            </p>

            <div style="
                background: #27ae60;
                color: white;
                padding: 14px;
                font-size: 26px;
                text-align: center;
                border-radius: 6px;
                letter-spacing: 4px;
                font-weight: bold;
                margin-top: 10px;
            ">
                {reset_code}
            </div>

            <p style="margin-top: 20px;">
                This verification code will expire in <strong>5 minutes</strong>.
            </p>

            <p>
                If you did not request a password reset, you may safely ignore this message.
            </p>

            <hr style="margin-top: 25px; border: none; border-top: 1px solid #ddd;">

            <p style="font-size: 12px; color: #888; text-align: center; margin-top: 15px;">
                © 2025 Campus E-Wallet System
            </p>

        </div>
    </body>
    </html>
    """

    # Construct email as multipart (plain text + HTML)
    email = MIMEMultipart("alternative")
    email["From"] = sender_email
    email["To"] = recipient_email
    email["Subject"] = subject

    email.attach(MIMEText(plain_text, "plain"))
    email.attach(MIMEText(html_content, "html"))

    # Establish secure SSL context and send the email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, email.as_string())

    return True
