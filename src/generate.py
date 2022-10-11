import glob
import os
from itertools import zip_longest
from PyPDF2 import PdfFileWriter, PdfFileReader
from os import makedirs, path

from data import FormData
from instance import instance_data


def fill(pdf_name: str, data: FormData, max_rate: float, fiscal_year: int, send_mail=False):
    pdf = PdfFileReader(open(pdf_name, "rb"), strict=False)
    if not path.exists('../out'):
        makedirs('../out')
    for f in glob.glob('out/*'):
        os.remove(f)
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
        for i, period in zip_longest(range(1, 5), sorted(child.periods.keys()), fillvalue=""):
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
            if send_mail and child.email:
                messages[child] = (form_id, fiscal_year)
    return messages
