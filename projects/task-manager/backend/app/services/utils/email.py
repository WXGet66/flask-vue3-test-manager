from flask_mail import Message
from app import mail

def send_email(subject, recipients, html_body):
    """
    发送邮件
    :param subject: 邮件主题
    :param recipients: 收件人列表，例如 ['user@example.com']
    :param html_body: HTML格式的邮件内容
    """
    msg = Message(subject, recipients=recipients, html=html_body)
    mail.send(msg)