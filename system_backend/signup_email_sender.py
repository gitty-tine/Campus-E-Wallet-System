"""
Account Verification Email Sender Module

This module is responsible for sending **account registration verification
emails** for the Campus E-Wallet System using Gmail’s SMTP service.

Main Responsibilities:
- Send email-based verification codes during account registration
- Provide both **plain text** and **HTML** email formats for compatibility
- Clearly display the verification code and its expiration time
- Use secure SSL-based SMTP communication with Gmail

Email Features:
- User-friendly HTML layout with highlighted verification code
- Fallback plain-text message for older or restricted email clients
- Clear instructions and security notice for unintended recipients

Security Notes:
- Uses SSL encryption for SMTP communication
- Requires an app-specific Gmail password (recommended)
- Handles email delivery only (verification logic is managed elsewhere)

Dependencies:
- smtplib and ssl for secure email transport
- email.mime for constructing multipart email messages

This module is intended to be called by signup or verification services
(e.g., student registration workflows) when a user requests
email-based account verification.
"""

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_verification_email(recipient_email, verification_code):
    """
    Send a registration verification email to a user.

    Parameters:
        recipient_email (str): Email address of the recipient.
        verification_code (str): Numeric or alphanumeric code to verify the account.

    Returns:
        bool: True if email is successfully sent.

    Raises:
        smtplib.SMTPException: If sending email fails due to SMTP issues.
    """
    # Sender credentials
    sender_email = "campus.ewallet@gmail.com"
    sender_password = "wmqs rvav eref zlkz"

    # Email subject
    subject = "Campus E-Wallet System - Register Account Verification"

    # Plain text version of the email (for clients that do not support HTML)
    plain_text = (
        f"Hello user,\n\n"
        f"Use this verification code to complete your account registration:\n\n"
        f"Verification Code: {verification_code}\n\n"
        f"This code is valid for 5 minutes.\n"
        f"If this wasn't you, please ignore this email.\n\n"
        f"Campus E-Wallet System Team"
    )

    # HTML version of the email with styling and prominent code display
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #e8f5e9; padding: 30px;">
        <div style="max-width: 480px; margin: auto; background: white; padding: 25px; border-radius: 10px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);">

            <h2 style="color: #2E7D32; text-align: center; margin-top: 10px;">
                Campus E-Wallet Verification
            </h2>

            <p>Hello user,</p>

            <p>
                To complete your registration, please use the verification code below:
            </p>

            <div style="
                background: #2E7D32;
                color: white;
                padding: 14px;
                font-size: 26px;
                text-align: center;
                border-radius: 6px;
                letter-spacing: 4px;
                font-weight: bold;
                margin-top: 10px;
            ">
                {verification_code}
            </div>

            <p style="margin-top: 20px;">
                This verification code will expire in <strong>5 minutes</strong>.
            </p>

            <p>
                If you did not request this code, you may safely ignore this message.
            </p>

            <hr style="margin-top: 25px; border: none; border-top: 1px solid #c8e6c9;">

            <p style="font-size: 12px; color: #777; text-align: center; margin-top: 15px;">
                © 2025 Campus E-Wallet System
            </p>

        </div>
    </body>
    </html>
    """

    # Construct the email message
    email = MIMEMultipart("alternative")
    email["From"] = sender_email
    email["To"] = recipient_email
    email["Subject"] = subject

    email.attach(MIMEText(plain_text, "plain"))
    email.attach(MIMEText(html_content, "html"))

    # Send the email via Gmail's SMTP server with SSL
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, email.as_string())

    return True
