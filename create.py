import generate
import gui
from data import FormData


def fill():
    if generate.fill('attest.pdf', FormData('lijst.xlsx'), gui.max_rate.get(), gui.fiscal_year.get(), gui.should_send_mail.get()):
        gui.confirm()
    else:
        gui.refuse()


if __name__ == "__main__":
    gui.pop(len(FormData('lijst.xlsx')))
