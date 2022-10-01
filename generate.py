import configparser
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from itertools import zip_longest
from PyPDF2 import PdfFileWriter, PdfFileReader
from data import FormData, Child
from instance import instance_data

mail_config = configparser.ConfigParser()
mail_config.read('smtp.ini')
login_data = mail_config['DEFAULT']


def fill(pdf_name: str, data: FormData, max_rate: float, fiscal_year: int, should_send_mail=False):
    pdf = PdfFileReader(open(pdf_name, "rb"), strict=False)
    messages = dict()
    for j, child in enumerate(data.children):
        pdf2 = PdfFileWriter()
        form_id = child.generate_id(fiscal_year, j)
        fields = instance_data()
        fields["name"] = child.name
        fields["firstName"] = child.first_name
        fields["birthdate"] = child.birthdate.strftime("%d/%m/%Y")
        fields["street"] = child.street
        fields["nr"] = child.nr
        fields["zip"] = child.zip
        fields["town"] = child.town
        fields["id"] = form_id
        fields["taxYear"] = fiscal_year
        total_price = 0
        for i, period in zip_longest(range(1, 5), child.periods.keys(), fillvalue=""):
            fields[f'period{i}'] = str(period)
            fields[f'period{i}Days'] = period.days if period else ""
            fields[f'period{i}Rate'] = "€ {:.2f}".format(period.rate(child.periods[period])) \
                if period and data.exceeds_rate(period, max_rate) else ""
            fields[f'period{i}Price'] = "€ {:.2f}".format(child.periods[period]) if period else ""
            total_price += child.periods[period] if period else 0
        fields["totalPrice"] = "€ {:.2f}".format(total_price)
        for page in range(2):
            pdf2.addPage(pdf.getPage(page))
            pdf2.updatePageFormFieldValues(pdf2.getPage(page), fields)
        pdf2.addPage(pdf.getPage(2))
        with open(f'out/{form_id}.pdf', "wb+") as filled:
            try:
                pdf2.write(filled)
            except IOError:
                return False
            if should_send_mail and child.email:
                messages[child] = (form_id, fiscal_year)
    send_mails(messages)
    return True


def build_mail(child: Child, fiscal_year: int, form_id: str):
    msg = MIMEMultipart()
    msg['From'] = login_data['username']
    msg['To'] = child.email
    if login_data['cc']:
        msg['Cc'] = login_data['cc']
    msg['Reply-To'] = login_data['reply_to'] if login_data['reply_to'] else login_data['username']
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = f"Fiscaal attest kinderopvang {fiscal_year}"
    with open('mailTemplate.html', 'r') as template:
        msg.attach(MIMEText(template.read().format(child.first_name, fiscal_year, login_data['reply_to']), 'html'))
    part = MIMEBase('application', "octet-stream")
    with open(f'out/{form_id}.pdf', 'rb') as file:
        part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={form_id}.pdf')
        msg.attach(part)
    return msg


def send_mails(messages: dict):
    server = smtplib.SMTP(login_data['server_name'], int(login_data['port']))
    server.starttls()
    server.login(login_data['username'], login_data['password'])
    for child, (form_id, fiscal_year) in messages.items():
        server.sendmail(login_data['username'], child.email, build_mail(child, fiscal_year, form_id).as_string())
        print(f'File sent to {child.email}')
    server.quit()
