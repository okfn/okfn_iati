import csv
import re
from enum import Enum

from okfn_iati.data import get_data_folder


class EnumFromCSV:
    def __init__(self, csv_filename, code_field='code', name_field='name'):
        self.csv_file = csv_filename
        self.csv_path = get_data_folder() / self.csv_file
        if self.csv_path is None or not self.csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")
        self._loaded = False
        self.code_field = code_field
        self.name_field = name_field
        self.data = {}

    def load_data(self):
        if self._loaded:
            return self.data

        with open(self.csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                code = row[self.code_field]
                self.data[code] = {
                    "name": row[self.name_field],
                }
                # A code and a name is required but we can have more data
                for key, value in row.items():
                    if key not in [self.code_field, self.name_field]:
                        self.data[code][key] = value

        self._loaded = True
        return self.data

    def __getitem__(self, code):
        if not self._loaded:
            self.load_data()
        if code not in self.data:
            class_name = self.__class__.__name__
            raise KeyError(f"Code not found: '{code}' for {class_name}")
        return self.data.get(code)

    @classmethod
    def to_enum(cls, enum_name, member_field=None, value_field=None):
        """
        Build a Python Enum from the CSV data.

        member_field: column to use for the enum member name (defaults to code_field)
        value_field:  column to use for the enum member value (defaults to code_field)
        """
        inst = cls()
        rows = inst.load_data()

        member_field = member_field or inst.code_field
        value_field = value_field or inst.code_field

        members = {}
        for code, row in rows.items():
            # Member (name of the enum item)
            member = row.get(member_field)

            # Fallback: if asking for 'EnumName' but it doesn't exist, derive from Name
            if not member and member_field == "EnumName" and "Name" in row:
                member = re.sub(r'[^A-Z0-9]+', '_', row["Name"].upper()).strip('_')

            # As last resort, allow using the code as member
            if not member and member_field == inst.code_field:
                member = code

            # Value of the enum item
            value = row.get(value_field)
            if value is None:
                if value_field == inst.code_field:
                    value = code
                elif value_field == inst.name_field:
                    value = row.get(inst.name_field)

            if member and value and member not in members:
                members[member] = value

        return Enum(enum_name, members)


class SectorCategoryData(EnumFromCSV):
    def __init__(self):
        super().__init__(csv_filename='sector-category-codes.csv', code_field='Code', name_field='Name')


class LocationTypeData(EnumFromCSV):
    def __init__(self):
        super().__init__(csv_filename='location-type-codes.csv', code_field='Code', name_field='Name')
