from threading import Thread
from flask import render_template
from flask_mail import Message
from app import app, mail
from app.models import Email


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(text_body, html_body, rec):
    msg = Message('Транснефть - Материалы', recipients=rec)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()

def send_email_to_everyone(material):
    recipients = []
    emails = Email.query.all()
    for e in emails:
        recipients.append(e.value)
    send_email(text_body=render_template('email/notification.txt', material=material),
               html_body=render_template('email/notification.html', material=material),
               rec=recipients)
