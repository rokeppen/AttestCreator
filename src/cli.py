import sys
import getopt
from datetime import datetime

from mail import send_mails
from data import FormData
from generate import fill


def main(argv):
    pdf = 'attest.pdf'
    persons = 'lijst.xlsx'
    should_send_mail = False
    tax_year = datetime.now().year
    max_rate = 14.4
    try:
        opts, _ = getopt.getopt(argv, "mp:l:y:r:", ["pdf=", "list=", "year=", "rate="])
    except getopt.GetoptError:
        print('cli.py -p <path-to-pdf> -l <path-to-excel> -y <fiscal-year> -r <max-reimbursement-rate>')
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
    send_mails(fill(pdf, FormData(persons), max_rate, tax_year, should_send_mail))


if __name__ == "__main__":
    main(sys.argv[1:])
