from pandas import to_datetime, isna, read_excel
from numpy import timedelta64
from collections import defaultdict

pb = [f"Begin periode {i}" for i in range(1, 5)]
pe = [f"Einde periode {i}" for i in range(1, 5)]
pp = [f"Prijs periode {i}" for i in range(1, 5)]


class Period:

    def __init__(self, start, end):
        self.start = to_datetime(start)
        self.end = to_datetime(end)
        self.days = (self.end - self.start).days + 1

    def rate(self, price: float):
        return price / self.days

    def overlaps(self, period):
        return self.start < period.start < self.end or self.start < period.end < self.end \
               or period.start < self.start < period.end

    def __lt__(self, other):
        return self.start < other.start

    def __eq__(self, other):
        return isinstance(other, Period) and self.start == other.start and self.end == other.end

    def __hash__(self):
        return hash(self.start) + hash(self.end) * 31

    def __str__(self):
        return f'{self.start.strftime("%d/%m/%Y")} - {self.end.strftime("%d/%m/%Y")}'

    def __repr__(self):
        return str(self)


class Person:

    def __init__(self, name: str, first_name: str):
        self.name = name
        self.first_name = first_name
        self.email = None
        self.street = None
        self.nr = None
        self.zip = None
        self.town = None
        self.nis = None

    def extra_data(self, row, suffix = ""):
        if not suffix:
            self.email = s(row["E-mail"])
        self.street = s(row["Straatnaam" + suffix])
        self.nr = s(row["Huisnummer" + suffix])
        self.zip = int(row["Postcode" + suffix]) if s(row["Postcode" + suffix]) else None
        self.town = s(row["Gemeente" + suffix])
        self.nis = s(row["Rrn" + suffix])

    def __eq__(self, other):
        return isinstance(other, Child) and self.name == other.name and self.first_name == other.first_name

    def __hash__(self):
        return hash(self.name) + hash(self.first_name) * 31

    def __str__(self):
        return f'{self.name}, {self.first_name}'


class Child(Person):

    def __init__(self, name: str, first_name: str, birthdate, parent: Person = None):
        super().__init__(name, first_name)
        self.birthdate = birthdate
        self.periods = dict()
        self.parent = parent

    def can_add_period(self, period: Period):
        return not any(p.overlaps(period) for p in self.periods)

    def add_period(self, period: Period, price: float):
        if not self.can_add_period(period):
            return False
        self.periods[period] = price
        return True

    def __repr__(self):
        return str(self) + ": " + str(self.periods)

    def generate_id(self, year, index):
        return (self.name[0] + self.first_name[0]).upper() + self.birthdate.strftime("%d%m%Y") + f'-{year}-{index}'


class FormData:

    def __init__(self, file_name: str):
        self.children = []
        self.periods = defaultdict(set)
        if not file_name:
            return
        self.df = read_excel(file_name)
        for j, row in self.df.iterrows():
            name = row["Naam"]
            first_name = row["Voornaam"]
            birthdate = row["Geboortedatum"]
            if isna(name) or isna(first_name) or isna(birthdate):
                continue
            child = Child(name, first_name, birthdate)
            child.extra_data(row)
            name_parent = row["Naam schuldenaar"]
            first_name_parent = row["Voornaam schuldenaar"]
            if not isna(name_parent) and not isna(first_name_parent):
                parent = Person(name_parent, first_name_parent)
                parent.extra_data(row, " schuldenaar")
                child.parent = parent
            for i in range(4):
                if not (isna(row[pb[i]]) or isna(row[pe[i]]) or isna(row[pp[i]])) and valid_age(row[pb[i]], birthdate):
                    period = Period(row[pb[i]], row[pe[i]])
                    if child not in self.children and child.add_period(period, row[pp[i]]):
                        self.periods[period].add(row[pp[i]])
                        self.children.append(child)
                    elif child in self.children:
                        known_children = [c for c in self.children if c == child]
                        if not all(c.can_add_period(period) for c in known_children):
                            continue
                        if all(len(c.periods) == 4 for c in known_children):
                            if child.add_period(period, row[pp[i]]):
                                self.periods[period].add(row[pp[i]])
                                self.children.append(child)
                        else:
                            known_child = next(filter(lambda c: len(c.periods) != 4, known_children), None)
                            if known_child.add_period(period, row[pp[i]]):
                                self.periods[period].add(row[pp[i]])
                                known_child.email = child.email if not known_child.email else known_child.email

    def __len__(self):
        return len(self.children)

    def __str__(self):
        return str(self.periods) + "\n" + "\n".join(repr(c) for c in self.children)

    def __repr__(self):
        return str(self)

    def exceeds_rate(self, period: Period, max_rate: float):
        return any(period.rate(price) > max_rate for price in self.periods[period])


def valid_age(c1, c2):
    return (c1 - c2) / timedelta64(1, 'Y') < 14


def s(val):
    return "" if isna(val) else val
