from flask_mail import Message
from flask import render_template
from app import app, mail, logger, REPO_NAME
import shutil
import os

EMAILS = os.environ.get('EMAILS').split(',')

def delete_repo():
    try:
        if os.path.exists(os.path.join(os.getcwd(), REPO_NAME)):
            logger.info(f"Deleting repo folder.")
            shutil.rmtree(REPO_NAME)
            logger.info(f"Repo folder successful deleted.")
    except:
        pass


def send_email(subject, html_page, stage):
    try:
        recipients = ' '.join([email.split('@')[0] for email in EMAILS])
        html_body = render_template(html_page, recipients=recipients, stage=stage)
        msg = Message(subject, recipients=EMAILS, html=html_body)
        mail.send(msg)
        logger.info(f"Email was sent successfully to {recipients}")
    except Exception as e:
        logger.error(f'Error sending email: {e}')

def copy_env(source_dir, dest_dir):
    env_files = {'weight.env', 'billing.env', 'nginx.conf'}
    for file in env_files:
        source_file = os.path.join(source_dir, file)
        dest_file = os.path.join(dest_dir, file)
        shutil.copy(source_file, dest_file)