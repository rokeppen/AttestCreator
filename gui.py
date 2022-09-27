from datetime import datetime
import create
from tkinter import *
from tkinter import ttk


win = Tk()
fiscal_year = IntVar()
max_rate = DoubleVar()
should_send_mail = IntVar()

def confirm():
    top = Toplevel(win)
    top.geometry("150x40")
    top.title("Bevestiging")
    Label(top, text="Genereren gelukt!").pack(pady=5)
    top.protocol("WM_DELETE_WINDOW", exit)


def refuse():
    top = Toplevel(win)
    top.geometry("150x80")
    top.title("Mislukt")
    Label(top, text="Er is een fout opgetreden!").pack(pady=5)
    ttk.Button(top, text="Sluit", command=exit).pack(pady=5)


def pop(attest: int):
    win.title("Genereer attesten")
    label_text = f"werden {attest} attesten" if attest != 1 else "werd 1 attest"
    Label(win, text=f"Er {label_text} gevonden om te genereren. Doorgaan?").grid(row=0, columnspan=2, padx=5)
    Label(win, text="Fiscaal jaar").grid(row=1)
    fiscal_year.set(datetime.now().year)
    Entry(win, textvariable=fiscal_year).grid(row=1, column=1)
    Label(win, text="Plafond:").grid(row=2)
    max_rate.set(14.40)
    Entry(win, textvariable=max_rate).grid(row=2, column=1)
    should_send_mail.set(0)
    ttk.Checkbutton(win, text="Verstuur via mail", variable=should_send_mail).grid(row=3, columnspan=2)
    ttk.Button(win, text="Genereer", command=create.fill).grid(row=4, columnspan=2, pady=5)
    win.mainloop()
