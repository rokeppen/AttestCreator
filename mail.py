import configparser
import smtplib
import socket
from time import time, sleep
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from tkinter import *

from numpy import Inf

from data import Child

parser = configparser.ConfigParser()
smtp_file_name = 'smtp.ini'
parser.read(smtp_file_name)


class SMTPData:

    def __init__(self):
        login_data = parser['DEFAULT']
        self.server_name = StringVar(value=login_data['server_name'])
        self.port = IntVar(value=int(login_data['port']))
        self.user = StringVar(value=login_data['username'])
        self.password = StringVar(value=login_data['password'])
        self.reply = StringVar(value=login_data['reply_to'] if login_data['reply_to'] else self.user.get())
        self.cc = StringVar(value=login_data['cc'])
        self.max_mails = IntVar(value=int(login_data['max_mails']) if login_data['max_mails'] else Inf)

    def validate(self):
        return self.server_name.get() and self.port.get() and self.user.get() and self.password.get()

    def test_connection(self):
        try:
            server = self.login(1)
            server.quit()
            return True
        except (socket.timeout, smtplib.SMTPAuthenticationError):
            return False

    def login(self, t=5):
        server = smtplib.SMTP(self.server_name.get(), self.port.get(), timeout=t)
        server.starttls()
        server.login(self.user.get(), self.password.get())
        return server

    def save(self):
        parser.set("DEFAULT", "server_name", self.server_name.get())
        parser.set("DEFAULT", "port", str(self.port.get()))
        parser.set("DEFAULT", "username", self.user.get())
        parser.set("DEFAULT", "password", self.password.get())
        parser.set("DEFAULT", "reply_to", self.reply.get())
        parser.set("DEFAULT", "cc", self.cc.get())
        parser.set("DEFAULT", "max_mails", str(self.max_mails.get()))
        with open(smtp_file_name, 'w') as config_file:
            parser.write(config_file)


def build_mail(data: SMTPData, child: Child, fiscal_year: int, form_id: str):
    msg = MIMEMultipart()
    msg['From'] = data.user.get()
    msg['To'] = child.email
    if data.cc.get():
        msg['Cc'] = data.cc.get()
    msg['Reply-To'] = data.reply.get()
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = f"Fiscaal attest kinderopvang {fiscal_year}"
    with open('mailTemplate.html', 'r') as template:
        msg.attach(MIMEText(template.read().format(child.first_name, fiscal_year), 'html'))
    part = MIMEBase('application', "octet-stream")
    with open(f'out/{form_id}.pdf', 'rb') as file:
        part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={form_id}.pdf')
        msg.attach(part)
    return msg


def send_mails(messages: dict, feedback=print, data: SMTPData = SMTPData()):
    server = data.login()
    start_time = time()
    current_max = data.max_mails.get()
    for i, child in enumerate(messages.keys()):
        passed_time = time() - start_time
        if i > current_max and passed_time < 60:
            feedback('Mailen gepauzeerd door maximaal aantal...')
            sleep(60 - passed_time)
            current_max += i - 1
        form_id, fiscal_year = messages[child]
        server.sendmail(data.user.get(), child.email, build_mail(data, child, fiscal_year, form_id).as_string())
        feedback(f'Mail {i}/{len(messages)} gestuurd naar {child.email}.')
    server.quit()
