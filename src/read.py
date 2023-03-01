from glob import glob
from PyPDF2 import PdfReader
import re
from data import FormData


def read(dir_name: str, data: FormData):
    df = data.df
    for pdf_name in glob(dir_name + '/*.pdf'):
        pdf = PdfReader(open(pdf_name, "rb"))
        fields = pdf.get_form_text_fields()
        try:
            id = fields["id"]
        except KeyError:
            print("fail: ", pdf_name, list(fields.keys()))
            continue
        print("success: ", pdf_name)
        fill(df, id, "Rrn", re.sub("[^0-9]", "", fields["nis"]))
        fill(df, id, "Naam", fields["name"])
        fill(df, id, "Voornaam", fields["firstName"])
        fill(df, id, "Geboortedatum", fields["birthdate"])
        fill(df, id, "Straatnaam", fields["street"])
        fill(df, id, "Huisnummer", fields["nr"])
        fill(df, id, "Postcode", fields["zip"])
        fill(df, id, "Gemeente", fields["town"])
        fill(df, id, "Rrn schuldenaar", re.sub("[^0-9]", "", fields["debtorNis"]))
        fill(df, id, "Naam schuldenaar", fields["debtorName"])
        fill(df, id, "Voornaam schuldenaar", fields["debtorFirstName"])
        fill(df, id, "Straatnaam schuldenaar", fields["debtorStreet"])
        fill(df, id, "Huisnummer schuldenaar", fields["debtorNr"])
        fill(df, id, "Postcode schuldenaar", fields["debtorZip"])
        fill(df, id, "Gemeente schuldenaar", fields["debtorTown"])
    df.to_excel('../test-filled.xlsx', index=False)

def fill(df, id, column, value):
    df.loc[df["Referentie"] == id, [column]] = value
    
if __name__ == '__main__':
    read('../in', FormData('../test.xlsx'))
