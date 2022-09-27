import generate
import gui


def fill():
    if generate.fill('attest.pdf', 'lijst.xlsx', gui.max_rate.get(), gui.fiscal_year.get(), gui.should_send_mail.get()):
        gui.confirm()
    else:
        gui.refuse()


if __name__ == "__main__":
    gui.pop(generate.count_data('lijst.xlsx'))
