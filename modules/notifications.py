"""
FAFO Alert & Notification Service
Sends automated email notifications upon new submissions and logs local alerts.
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from pathlib import Path
from config.settings import (
    SMTP_ENABLED, SMTP_SERVER, SMTP_PORT, SMTP_USERNAME,
    SMTP_PASSWORD, SMTP_FROM_EMAIL, NOTIFICATION_LOG_FILE
)

def send_submission_alert(
    incident_key: str,
    title: str,
    severity: str,
    submitter_name: str,
    submitter_email: str
) -> bool:
    """
    Sends alerts to system reviewers/administrators when a new incident is submitted.
    Uses SMTP email if enabled; otherwise, writes formatted mock emails to the
    offline `logs/notifications.log` file.
    """
    subject = f"[FAFO ALERT] New Forensic Incident Logged: {incident_key}"
    
    # HTML Email body
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f6f9; padding: 20px; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border: 1px solid #ddd; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                <div style="background-color: #0b172a; padding: 20px; text-align: center; color: #00e5ff;">
                    <h2 style="margin: 0; font-size: 24px; letter-spacing: 1px;">FAFO digital forensics</h2>
                    <p style="margin: 5px 0 0 0; color: #a2b0c4; font-size: 14px;">Incident Preservation Alert</p>
                </div>
                <div style="padding: 24px;">
                    <p style="font-size: 16px; margin-top: 0;">A new incident has been uploaded to the FAFO preservation vault:</p>
                    <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold; border-bottom: 1px solid #eee; width: 140px;">Incident Key:</td>
                            <td style="padding: 8px 0; border-bottom: 1px solid #eee; color: #008ca8; font-family: monospace; font-size: 15px;">{incident_key}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold; border-bottom: 1px solid #eee;">Title:</td>
                            <td style="padding: 8px 0; border-bottom: 1px solid #eee;">{title}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold; border-bottom: 1px solid #eee;">Severity:</td>
                            <td style="padding: 8px 0; border-bottom: 1px solid #eee;">
                                <span style="padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; 
                                             background-color: {'#ff3860' if severity == 'Critical' else '#ff9f1c' if severity == 'High' else '#3273dc' if severity == 'Medium' else '#23d160'}; 
                                             color: white;">
                                    {severity}
                                </span>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold; border-bottom: 1px solid #eee;">Submitter:</td>
                            <td style="padding: 8px 0; border-bottom: 1px solid #eee;">{submitter_name} ({submitter_email})</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: bold; border-bottom: 1px solid #eee;">Timestamp:</td>
                            <td style="padding: 8px 0; border-bottom: 1px solid #eee;">{datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}</td>
                        </tr>
                    </table>
                    <p style="margin-bottom: 0;">Please log into the FAFO portal as a Reviewer/Admin to audit case evidence and authorize legal-ready exports.</p>
                </div>
                <div style="background-color: #f8f9fa; padding: 15px; text-align: center; border-top: 1px solid #eee; font-size: 12px; color: #777;">
                    Security Note: This is an automated email from FAFO secure vault. Do not reply directly.
                </div>
            </div>
        </body>
    </html>
    """
    
    # 1. SMTP Email Sending
    if SMTP_ENABLED:
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = SMTP_FROM_EMAIL
            msg['To'] = SMTP_USERNAME # Sends to system account (acting as admin)
            
            part = MIMEText(html_body, 'html')
            msg.attach(part)
            
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.sendmail(SMTP_FROM_EMAIL, [SMTP_USERNAME], msg.as_string())
                
            logging.info(f"Notification email sent successfully for {incident_key}")
            
        except Exception as e:
            logging.error(f"SMTP notification failed: {str(e)}")
            # Fallback will write to file log anyway
            
    # 2. Write to local offline log file (Always happens as local audit/testing support)
    try:
        timestamp_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        log_line = (
            f"[{timestamp_str}] EMAIL OUTBOX | "
            f"TO: admins@fafo.local | "
            f"SUBJECT: {subject} | "
            f"BODY SUMMARY: Submitter={submitter_name}, Severity={severity}, Title='{title}'\n"
        )
        
        with open(NOTIFICATION_LOG_FILE, "a") as f:
            f.write(log_line)
            
        return True
    except Exception as e:
        logging.error(f"Failed to write mock notification log: {str(e)}")
        return False
