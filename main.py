import csv
import smtplib
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from os import getcwd
from os.path import normpath, join

from PyPDF2 import PdfFileWriter, PdfFileReader
from PyPDF2.generic import BooleanObject, NameObject, IndirectObject
import configparser


config = configparser.ConfigParser()
config.read('smtp.ini')
login_data = config['DEFAULT']
date_format = "%d/%m/%Y"


def set_need_appearances_writer(writer: PdfFileWriter):
    try:
        catalog = writer._root_object
        if "/AcroForm" not in catalog:
            writer._root_object.update({NameObject("/AcroForm"): IndirectObject(len(writer._objects), 0, writer)})
        need_appearances = NameObject("/NeedAppearances")
        writer._root_object["/AcroForm"][need_appearances] = BooleanObject(True)
        return writer

    except Exception as e:
        print('set_need_appearances_writer() catch : ', repr(e))
        return writer


def fill(pdf_name: str, csv_name, max_rate: int, fiscal_year: int, send_mail=False):
    pdfin = normpath(join(getcwd(), pdf_name))
    pdf = PdfFileReader(open(pdfin, "rb"), strict=False)
    if "/AcroForm" in pdf.trailer["/Root"]:
        pdf.trailer["/Root"]["/AcroForm"].update(
            {NameObject("/NeedAppearances"): BooleanObject(True)})
    with open(csv_name, 'r') as csv_file:
        for j, row in enumerate(csv.reader(csv_file, delimiter=';')):
            pdf2 = PdfFileWriter()
            set_need_appearances_writer(pdf2)
            if "/AcroForm" in pdf2._root_object:
                pdf2._root_object["/AcroForm"].update(
                    {NameObject("/NeedAppearances"): BooleanObject(True)})
            birthdate = datetime.strptime(row[2], date_format)
            form_id = row[0][0].upper() + row[1][0].upper() + birthdate.strftime("%d%m%Y") + "-" + str(
                fiscal_year) + "-" + str(j + 1)
            field_dictionary = {"name": str(row[0]),
                                "firstName": row[1],
                                "birthdate": birthdate,
                                "street": row[3],
                                "nr": row[4],
                                "zip": row[5],
                                "town": row[6],
                                "id": form_id,
                                "taxYear": fiscal_year
                                }
            price_total = 0
            for i in range(8, len(list(filter(None, row))) - 1, 3):
                period_nr = str((i - 7) // 3 + 1)
                period_from = datetime.strptime(row[i], date_format)
                period_to = datetime.strptime(row[i + 1], date_format)
                period_price = float(row[i + 2])
                period_days = (period_to - period_from).days + 1
                period_rate = period_price / period_days
                price_total += period_price
                field_dictionary[
                    "period" + period_nr] = f'{period_from.strftime(date_format)} - {period_to.strftime(date_format)}'
                field_dictionary["period" + period_nr + "Days"] = period_days
                field_dictionary["period" + period_nr + "Rate"] = "€ " + "{:.2f}".format(
                    period_rate) if period_rate > max_rate else ""
                field_dictionary["period" + period_nr + "Price"] = "€ " + "{:.2f}".format(period_price)
            field_dictionary["totalPrice"] = "€ " + "{:.2f}".format(price_total)
            for page in range(pdf.getNumPages() - 1):
                pdf2.addPage(pdf.getPage(page))
                pdf2.updatePageFormFieldValues(pdf2.getPage(page), field_dictionary)
            attest_name = form_id + '.pdf'
            with open('out/' + attest_name, "wb+") as filled:
                pdf2.write(filled)
            if send_mail:
                send_mail(row[7], attest_name)


def send_mail(to: str, file_name):
    msg = MIMEMultipart()
    msg['From'] = login_data['username']
    msg['To'] = to
    msg['Reply-To'] = login_data['reply_to']
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = "Dit is een test"
    msg.attach(MIMEText("Testmail"))
    part = MIMEBase('application', "octet-stream")
    with open(file_name, 'rb') as file:
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


if __name__ == '__main__':
    fill("Fiscaal attest kinderopvang.pdf", "test.txt", 14, 2022)
