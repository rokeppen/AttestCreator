from datetime import datetime
from glob import glob
from itertools import zip_longest
from PyPDF2 import PdfFileReader, PdfFileWriter
from io import BytesIO
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter
from os import makedirs, path, remove

from data import FormData
from instance import instance_data


def fill(pdf_name: str, data: FormData, max_rate: float, fiscal_year: int, signed=False):
    pdf = PdfFileReader(open(pdf_name, "rb"))
    target_dir = "signed" if signed else "out"
    if not path.exists(f'../{target_dir}'):
        makedirs(f'../{target_dir}')
    for f in glob(f'{target_dir}/*'):
        remove(f)
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
        fields["nis"] = child.nis
        if child.parent:
            fields["debtorName"] = child.parent.name
            fields["debtorFirstName"] = child.parent.first_name
            fields["debtorStreet"] = child.parent.street
            fields["debtorNr"] = child.parent.nr
            fields["debtorZip"] = child.parent.zip
            fields["debtorTown"] = child.parent.town
            fields["debtorNis"] = child.parent.nis
        elif signed:
            continue
        fields["id"] = form_id
        fields["taxYear"] = fiscal_year
        total_price = 0
        for i, period in zip_longest(range(1, 5), sorted(child.periods.keys()), fillvalue=""):
            fields[f'period{i}'] = str(period)
            fields[f'period{i}Days'] = period.days if period else ""
            fields[f'period{i}Rate'] = "€ {:.2f}".format(period.rate(child.periods[period])) \
                if period and data.exceeds_rate(period, max_rate) else ""
            fields[f'period{i}Price'] = "€ {:.2f}".format(child.periods[period]) if period else ""
            total_price += child.periods[period] if period else 0
        fields["totalPrice"] = "€ {:.2f}".format(total_price)
        if signed:
            fields["location"] = fields["instanceTown"]
            fields["authorizationDate"] = datetime.now().strftime("%d/%m/%Y")
            fields["authorizer"] = fields["instanceAuthorizer"]
        pdf2.add_page(pdf.pages[0])
        pdf2.update_page_form_field_values(pdf2.pages[0], fields)
        page2 = pdf.pages[1]
        if signed:
            page2.merge_page(signature())
        pdf2.add_page(page2)
        pdf2.update_page_form_field_values(pdf2.pages[1], fields)          
        pdf2.add_page(pdf.pages[2])
        with open(f'../{target_dir}/{form_id}.pdf', "wb+") as filled:
            try:
                pdf2.write(filled)
            except IOError:
                return False
            if child.email:
                messages[child] = (form_id, fiscal_year)
    return messages

def signature():
    packet = BytesIO()
    can = Canvas(packet, pagesize=letter)
    can.drawImage('config/signature.png', 279, 117, 226, 53, preserveAspectRatio=True)
    can.save()
    packet.seek(0)
    return PdfFileReader(packet).pages[0]
    
if __name__ == '__main__':
    fill('resources/attest.pdf', FormData('../test-filled.xlsx'), 50, 2022, True)
