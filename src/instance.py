from configparser import RawConfigParser
from os import path
from tkinter import *

parser = RawConfigParser()
parser.optionxform = str
config_file_name = path.join(path.dirname(__file__), 'config', 'instance.ini')
parser.read(config_file_name)


def instance_data():
    x = {"instance" + k: v for k, v in parser['INSTANCE'].items()}
    y = {"certifier" + k: v for k, v in parser['CERTIFIER'].items()}
    return x | y


class ConfigData:

    def __init__(self, section):
        self.section = section.upper()
        instance = parser[section]
        self.name = StringVar(value=instance["Name"])
        self.kbo = StringVar(value=instance["KBO"])
        self.street = StringVar(value=instance["Street"])
        self.nr = StringVar(value=instance["Nr"])
        self.zip = StringVar(value=instance["Zip"])
        self.town = StringVar(value=instance["Town"])

    def is_instance(self):
        return self.section == "INSTANCE"

    def save(self):
        parser.set(self.section, "Name", self.name.get())
        parser.set(self.section, "KBO", self.kbo.get())
        parser.set(self.section, "Street", self.street.get())
        parser.set(self.section, "Nr", self.nr.get())
        parser.set(self.section, "Zip", self.zip.get())
        parser.set(self.section, "Town", self.town.get())
        with open(config_file_name, 'w') as config_file:
            parser.write(config_file)
