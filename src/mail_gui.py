from tkinter import *

from numpy import Inf

from mail import SMTPData


class SMTPEdit(SMTPData):

    def __init__(self):
        super().__init__()
        self.server_name_var = StringVar(value=self.server_name)
        self.port_var = IntVar(value=self.port)
        self.user_var = StringVar(value=self.user)
        self.password_var = StringVar(value=self.password)
        self.reply_var = StringVar(value=self.reply)
        self.cc_var = StringVar(value=self.cc)
        self.max_mails_var = IntVar(value=self.max_mails if self.max_mails != Inf else None)

    def save(self):
        self.server_name = self.server_name_var.get()
        self.port = self.port_var.get()
        self.user = self.user_var.get()
        self.password = self.password_var.get()
        self.reply = self.reply_var.get()
        self.cc = self.cc_var.get()
        self.max_mails = self.max_mails_var.get() if self.max_mails_var.get() != 0 else None
        super().save()
