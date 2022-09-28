import configparser
import getopt
import smtplib
import sys
import numpy as np
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from os import getcwd
from os.path import normpath, join

import pandas as pd
from PyPDF2 import PdfFileWriter, PdfFileReader
from PyPDF2.generic import BooleanObject, NameObject, IndirectObject


mail_config = configparser.ConfigParser()
mail_config.read('smtp.ini')
login_data = mail_config['DEFAULT']
instance_config = configparser.ConfigParser()
instance_config.read('instance.ini')
instance_data = instance_config['DEFAULT']
date_format = "%d/%m/%Y"


def set_need_appearances_writer(writer: PdfFileWriter):
    try:
        if "/AcroForm" not in writer._root_object:
            writer._root_object.update({NameObject("/AcroForm"): IndirectObject(len(writer._objects), 0, writer)})
        need_appearances = NameObject("/NeedAppearances")
        writer._root_object["/AcroForm"][need_appearances] = BooleanObject(True)
    except Exception as e:
        print('set_need_appearances_writer() catch : ', repr(e))
    return writer


def count_data(list_file_name: str):
    df = pd.read_excel(list_file_name)
    return len(df.loc[(df["Begin periode 1"] - df["Geboortedatum"]) / np.timedelta64(1, 'Y') < 14])


def fill(pdf_name: str, list_file_name: str, max_rate: float, fiscal_year: int, should_send_mail=False):
    pdfin = normpath(join(getcwd(), pdf_name))
    pdf = PdfFileReader(open(pdfin, "rb"), strict=False)
    if "/AcroForm" in pdf.trailer["/Root"]:
        pdf.trailer["/Root"]["/AcroForm"].update({NameObject("/NeedAppearances"): BooleanObject(True)})
    df = pd.read_excel(list_file_name)
    for j, row in df.loc[(df["Begin periode 1"] - df["Geboortedatum"]) / np.timedelta64(1, 'Y') < 14].iterrows():
        pdf2 = PdfFileWriter()
        set_need_appearances_writer(pdf2)
        if "/AcroForm" in pdf2._root_object:
            pdf2._root_object["/AcroForm"].update({NameObject("/NeedAppearances"): BooleanObject(True)})
        name = row["Naam"]
        first_name = row["Voornaam"]
        birthdate = row["Geboortedatum"]
        form_id = name[0].upper() + first_name[0].upper() + birthdate.strftime("%d%m%Y") + "-" + str(fiscal_year) + "-" + str(j + 1)
        field_dictionary = {"instanceName": instance_data["naam"],
                            "instanceKBO": instance_data["kbo"],
                            "instanceStreet": instance_data["straat"],
                            "instanceNr": instance_data["nr"],
                            "instanceZip": instance_data["postcode"],
                            "instanceTown": instance_data["gemeente"],
                            "certifierName": instance_data["naam.certificering"],
                            "certifierKBO": instance_data["kbo.certificering"],
                            "certifierStreet": instance_data["straat.certificering"],
                            "certifierNr": instance_data["nr.certificering"],
                            "certifierZip": instance_data["postcode.certificering"],
                            "certifierTown": instance_data["gemeente.certificering"],
                            "name": name,
                            "firstName": first_name,
                            "birthdate": birthdate.strftime(date_format),
                            "street": row["Straatnaam"],
                            "nr": row["Huisnummer"],
                            "zip": int(row["Postcode"]),
                            "town": row["Gemeente"],
                            "id": form_id,
                            "taxYear": fiscal_year}
        price_total = 0
        exceeds_rate = {i: len(df.loc[df["Prijs periode " + str(i)] > max_rate]) > 0 for i in range(1, 5)}
        print({i: len(df.loc[df["Prijs periode " + str(i)] > max_rate]) for i in range(1, 5)})
        for i in range(8, len(row) - 1, 3):
            k = (i - 7) // 3 + 1
            period_from = row[i]
            period_to = row[i + 1]
            period_price = float(row[i + 2])
            period_days = (pd.to_datetime(period_to) - pd.to_datetime(period_from)).days + 1
            period_rate = period_price / period_days
            if not pd.isna(period_from) and (period_from - birthdate) / np.timedelta64(1, 'Y') < 14:
                price_total += period_price
                field_dictionary[f'period{k}'] = f'{period_from.strftime(date_format)} - {period_to.strftime(date_format)}'
                field_dictionary[f'period{k}Days'] = period_days
                field_dictionary[f'period{k}Rate'] = "€ {:.2f}".format(period_rate) if exceeds_rate[k] else ""
                field_dictionary[f'period{k}Price'] = "€ {:.2f}".format(period_price)
            else:
                field_dictionary[f'period{k}'] = ""
                field_dictionary[f'period{k}Days'] = ""
                field_dictionary[f'period{k}Rate'] = ""
                field_dictionary[f'period{k}Price'] = ""
        field_dictionary["totalPrice"] = "€ {:.2f}".format(price_total)
        for page in range(pdf.getNumPages()):
            pdf2.addPage(pdf.getPage(page))
            pdf2.updatePageFormFieldValues(pdf2.getPage(page), field_dictionary)
        attest_name = form_id + '.pdf'
        with open('out/' + attest_name, "wb+") as filled:
            pdf2.write(filled)
        if should_send_mail and not pd.isna(row["E-mail"]):
            send_mail(row["E-mail"], fiscal_year, first_name, attest_name)
    return True


def send_mail(to: str, fiscal_year: int, name: str, file_name):
    msg = MIMEMultipart()
    msg['From'] = login_data['username']
    msg['To'] = to
    if login_data['cc'] != "":
        msg['Cc'] = login_data['cc']
    msg['Reply-To'] = login_data['reply_to']
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = f"Fiscaal attest kinderopvang {fiscal_year}"
    with open('mailTemplate.html', 'r') as template:
        msg.attach(MIMEText(template.read().format(name, fiscal_year, login_data['reply_to'], instance_data['naam']), 'html'))
    part = MIMEBase('application', "octet-stream")
    with open('out/' + file_name, 'rb') as file:
        part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename={}'.format(file_name))
        msg.attach(part)
    server = smtplib.SMTP(login_data['server_name'], int(login_data['port']))
    server.starttls()
    server.login(login_data['username'], login_data['password'])
    server.sendmail(login_data['username'], to, msg.as_string())
    print(f'File sent to {to}')
    server.quit()


def main(argv):
    pdf = 'attest.pdf'
    persons = 'lijst.xlsx'
    should_send_mail = False
    tax_year = datetime.now().year
    max_rate = 14.4
    try:
        opts, args = getopt.getopt(argv, "mp:l:y:r:", ["pdf=", "list=", "year=", "rate="])
    except getopt.GetoptError:
        print('generate.py -p <pdf-form> -l <member list> -y <fiscal-year> -r <maximum reimbursement rate>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-p", "--pdf"):
            pdf = arg
        elif opt in ("-l", "--list"):
            persons = arg
        elif opt in ("-y", "--year"):
            tax_year = int(arg)
        elif opt == '-m':
            should_send_mail = True
        elif opt in ("-r", "--rate"):
            max_rate = float(arg.replace(',', '.'))
    fill(pdf, persons, max_rate, tax_year, should_send_mail)


if __name__ == "__main__":
    main(sys.argv[1:])
