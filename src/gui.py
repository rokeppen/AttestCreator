from datetime import datetime
from tkinter import *
from tkinter import ttk, filedialog
from idlelib.tooltip import Hovertip
from threading import Thread
from shutil import make_archive
from os import replace

import generate as g
from mail import SMTPData, send_mails
from data import FormData
from instance import ConfigData
from mail_gui import SMTPEdit

win = Tk()
fiscal_year = IntVar(value=datetime.now().year)
max_rate = DoubleVar(value=14.40)
send_mail = IntVar(value=0)


def ongoing(window):
    top = show(window, "Bezig", True)
    label = Label(top, text="Bezig met genereren...")
    label.pack(padx=5, pady=5)
    return label, top


def confirm(window):
    top = show(window, "Bevestiging", True)
    Label(top, text="Genereren gelukt!").grid(columnspan=2, padx=5, pady=5)
    ttk.Button(top, text="Sla attesten op", command=lambda: zip_and_remove(top)).grid(row=1, padx=5, pady=5)
    ttk.Button(top, text="Sluit", command=lambda: top.destroy()).grid(row=1, column=1, padx=5, pady=5)


def refuse(window):
    top = show(window, "Mislukt", True)
    Label(top, text="Er is een fout opgetreden!").pack(padx=5, pady=5)


def complain(window):
    top = show(window, "Geen attesten", True)
    Label(top, text="Er werden geen attesten gevonden om te genereren!").pack(padx=5, pady=5)


def generate():
    data = FormData(filedialog.askopenfilename())
    if not len(data):
        complain(win)
        return
    generate_win = show(win, "Genereer attesten")
    label_text = f"werden {len(data)} attesten" if len(data) > 1 else "werd 1 attest"
    Label(generate_win, text=f"Er {label_text} gevonden om te genereren. Doorgaan?").grid(row=0, columnspan=2, padx=5)
    labeled_entry(generate_win, "Fiscaal jaar:", fiscal_year, 1)
    labeled_entry(generate_win, "Plafond:", max_rate, 2)
    ttk.Checkbutton(generate_win, text="Verstuur via mail", variable=send_mail, state=NORMAL if SMTPData().test_connection() else DISABLED).grid(row=3, columnspan=2)
    ttk.Button(generate_win, text="Genereer", command=lambda: fill(data, generate_win)).grid(row=4, columnspan=2, pady=5)


def pop():
    win.title("AttestCreator")
    win.iconbitmap(default='src/resources/img/icon.ico')
    Label(win, text="Wat wil je doen?").grid(row=0, columnspan=3, padx=5)
    ttk.Button(win, text="Wijzig instellingen", command=configure).grid(row=1, column=0, pady=5)
    ttk.Button(win, text="Genereer attesten", command=generate).grid(row=1, column=1, pady=5)
    sign_button = ttk.Button(win, text="Teken attesten", state=DISABLED)
    sign_button.grid(row=1, column=2, pady=5)
    Hovertip(sign_button, 'Coming soon!', hover_delay=0)
    win.mainloop()


def configure():
    choice_window = show(win, "Configuratie")
    ttk.Button(choice_window, text="Gegevens vereniging", command=lambda: edit_config(ConfigData("INSTANCE"))).grid(row=1, column=0, pady=5)
    ttk.Button(choice_window, text="Gegevens certificeerder", command=lambda: edit_config(ConfigData("CERTIFIER"))).grid(row=1, column=1, pady=5)
    ttk.Button(choice_window, text="Configuratie mailing", command=lambda: edit_smtp(SMTPEdit())).grid(row=1, column=2, pady=5)


def fill(data: FormData, window):
    messages = g.fill('src/resources/attest.pdf', data, max_rate.get(), fiscal_year.get(), send_mail.get())
    label, top = ongoing(window)
    if not send_mail.get():
        close_callback(top, window)
        return
    try:
        Thread(target=lambda: worker(messages, label, top, window)).start()
    except Exception:
        refuse(window)


def worker(messages, label, top, window):
    send_mails(messages, lambda t: label.config(text=t))
    close_callback(top, window)


def close_callback(top, window):
    top.destroy()
    confirm(window)


def edit_config(data: ConfigData):
    label_text = "vereniging" if data.is_instance() else "certificeerder"
    config_window = show(win, "Configuratie" + label_text)
    Label(config_window, text=f"Bewerk de gegevens van de {label_text}:").grid(row=0, columnspan=2, padx=5)
    labeled_entry(config_window, "Naam:", data.name, 1)
    labeled_entry(config_window, "KBO:", data.kbo, 2)
    labeled_entry(config_window, "Straatnaam:", data.street, 3)
    labeled_entry(config_window, "Huisnummer:", data.nr, 4)
    labeled_entry(config_window, "Postcode:", data.zip, 5)
    labeled_entry(config_window, "Gemeente:", data.town, 6)
    ttk.Button(config_window, text="Sla op", command=lambda: save_and_close(config_window, data))\
        .grid(row=7, columnspan=2, pady=5)


def edit_smtp(data: SMTPEdit):
    smtp_window = show(win, "Mailconfiguratie")
    labeled_entry(smtp_window, "Server:", data.server_name_var, 0)
    labeled_entry(smtp_window, "Poort:", data.port_var, 1)
    labeled_entry(smtp_window, "Gebruikersnaam:", data.user_var, 2)
    labeled_entry(smtp_window, "Wachtwoord:", data.password_var, 3)
    labeled_entry(smtp_window, "Antwoord naar:", data.reply_var, 4)
    labeled_entry(smtp_window, "Cc:", data.cc_var, 5)
    labeled_entry(smtp_window, "Mails/minuut:", data.max_mails_var, 6)
    ttk.Button(smtp_window, text="Sla op", command=lambda: save_and_close(smtp_window, data))\
        .grid(row=7, columnspan=2, pady=5)


def show(parent, title, modal=False):
    window = Toplevel(parent)
    window.title(title)
    #if modal:
    #    window.transient(window)
    #    window.grab_set()
    return window


def save_and_close(window, data):
    data.save()
    window.destroy()


def labeled_entry(window, label: str, var, row: int):
    Label(window, text=label).grid(row=row, padx=5, pady=5)
    Entry(window, textvariable=var, width=100).grid(row=row, column=1, padx=5, pady=5)


def zip_and_remove(window):
    tmp_name = make_archive('attesten', 'zip', '../out')
    new_name = filedialog.askdirectory()
    if new_name:
        replace(tmp_name, new_name + '/attesten.zip')
    window.destroy()


if __name__ == "__main__":
    pop()
