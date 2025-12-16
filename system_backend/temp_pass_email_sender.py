"""
Temporary Password Email Sender Module

This module is responsible for sending a temporary password email to a student
after their Campus E-Wallet account has been created by an administrator.

Main Responsibilities:
- Compose a professional email containing a temporary password
- Send both plain-text and HTML email versions
- Connect securely to Gmail SMTP using SSL
- Deliver credentials safely to the student's registered email address

Security Notes:
- The temporary password should be changed immediately upon first login
- Uses Gmail App Password authentication (recommended over raw passwords)

Dependencies:
- smtplib, ssl: for secure SMTP communication
- email.mime.multipart, email.mime.text: for multi-format email content
"""

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_temp_password(recipient_email, student_name, temp_password):
    """
    Send a temporary password email to a student.

    Parameters:
        recipient_email (str): Email address of the student.
        student_name (str): Full name of the student.
        temp_password (str): Temporary password assigned to the student.

    Returns:
        bool: True if the email was successfully sent.

    Raises:
        smtplib.SMTPException: If sending email fails due to SMTP issues.
    """
    # Sender credentials
    sender_email = "campus.ewallet@gmail.com"
    sender_password = "temporary password to protect the account"

    # Email subject
    subject = "Campus E-Wallet System – Temporary Password Notification"

    # Plain text version
    plain_text = (
        f"Dear {student_name},\n\n"
        f"Your Campus E-Wallet account has been successfully created.\n"
        f"Temporary Password: {temp_password}\n\n"
        f"For security purposes, please log in and change your password immediately.\n\n"
        f"Best regards,\n"
        f"Campus E-Wallet System Team"
    )

    # HTML version
    html_content = f"""
    <html>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; background-color: #f0fdf4; padding: 30px;">
        <div style="max-width:500px; margin:auto; background:white; padding:30px;
                    border-radius:12px; box-shadow:0 3px 12px rgba(0,0,0,0.1);">

            <h2 style="color:#2E7D32; text-align:center; font-weight:bold; margin-bottom:20px;">
                Campus E-Wallet Account Created
            </h2>

            <p>Dear <strong>{student_name}</strong>,</p>

            <p>We are pleased to inform you that your Campus E-Wallet account has been successfully created. 
            Please use the temporary password below to log in:</p>

            <div style="
                background:#2E7D32;
                color:white;
                padding:16px;
                font-size:20px;
                text-align:center;
                border-radius:8px;
                font-weight:bold;
                margin:20px 0;
                letter-spacing:1px;
            ">
                {temp_password}
            </div>

            <p>For your security, it is mandatory to change your password immediately after logging in.</p>

            <p>Should you have any questions, please contact the Campus E-Wallet support team.</p>

            <hr style="margin-top:25px; border:none; border-top:1px solid #c8e6c9;">
            <p style="font-size:12px; text-align:center; color:#555;">
                © 2025 Campus E-Wallet System. All rights reserved.
            </p>
        </div>
    </body>
    </html>
    """

    # Create a multipart email with both plain-text and HTML
    email = MIMEMultipart("alternative")
    email["From"] = sender_email
    email["To"] = recipient_email
    email["Subject"] = subject

    email.attach(MIMEText(plain_text, "plain"))
    email.attach(MIMEText(html_content, "html"))

    # # Send email securely using SSL
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, email.as_string())

    return True
