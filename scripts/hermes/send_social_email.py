#!/usr/bin/env python3
"""
Deterministic Social Media Questions emailer. Emails today's social media
posts file to hello@phantom-byte.com. Idempotent: tracks a sent-marker so it
never emails the same day's file twice, even if called by both the agent cron
and the backstop cron.

Usage:
    python3 ~/send_social_email.py [path_to_posts_file]

If no path is given, it looks for today's file in the standard locations:
    ~/social_media_posts_YYYY-MM-DD.txt
    /mnt/c/Users/<user>/OneDrive/Desktop/TODAYS DATA FILES/social_media_posts_YYYY-MM-DD.txt
"""
import smtplib
import os
import sys
import glob
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

TO = "hello@phantom-byte.com"
FROM = "hello@phantom-byte.com"
SMTP_HOST = "smtp.ionos.com"
SMTP_PORT = 587
SMTP_USER = "hello@phantom-byte.com"
SMTP_PASS = "VJBvjbhydro1202$$"
SEARCH_DIRS = [
    "~",
    "/mnt/c/Users/<user>/OneDrive/Desktop/TODAYS DATA FILES",
]
MARKER_DIR = "~/cron/sent_markers"


def find_today_file():
    today = date.today().isoformat()
    for d in SEARCH_DIRS:
        exact = os.path.join(d, f"social_media_posts_{today}.txt")
        if os.path.exists(exact):
            return exact
    # fallback: newest social_media_posts_*.txt across search dirs
    matches = []
    for d in SEARCH_DIRS:
        matches += glob.glob(os.path.join(d, "social_media_posts_*.txt"))
    if matches:
        return max(matches, key=os.path.getmtime)
    return None


def already_sent(filepath):
    os.makedirs(MARKER_DIR, exist_ok=True)
    marker = os.path.join(MARKER_DIR, os.path.basename(filepath) + ".sent")
    return os.path.exists(marker)


def mark_sent(filepath):
    os.makedirs(MARKER_DIR, exist_ok=True)
    marker = os.path.join(MARKER_DIR, os.path.basename(filepath) + ".sent")
    with open(marker, "w") as f:
        f.write("sent")


def send_email(filepath):
    msg = MIMEMultipart()
    msg["From"] = FROM
    msg["To"] = TO
    msg["Subject"] = f"Social Media Questions - {date.today().isoformat()}"
    msg.attach(MIMEText("Today's social media questions are attached.", "plain"))
    with open(filepath, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        filename = os.path.basename(filepath)
        part.add_header("Content-Disposition", f"attachment; filename={filename}")
        msg.attach(part)
    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=60)
    server.starttls()
    server.login(SMTP_USER, SMTP_PASS)
    server.send_message(msg)
    server.quit()
    return True


def main():
    filepath = sys.argv[1] if len(sys.argv) > 1 else find_today_file()
    if not filepath or not os.path.exists(filepath):
        print("ERROR: no social media posts file found to email")
        sys.exit(1)
    if already_sent(filepath):
        print(f"SKIP: {os.path.basename(filepath)} already emailed")
        sys.exit(0)
    send_email(filepath)
    mark_sent(filepath)
    print(f"EMAIL SENT: {os.path.basename(filepath)} to {TO}")


if __name__ == "__main__":
    main()
