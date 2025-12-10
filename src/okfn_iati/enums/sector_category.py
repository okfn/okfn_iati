import csv
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
    def to_enum(cls, enum_name):
        data = cls().load_data()
        # Remove duplicates, keep first name for each category code
        enum_dict = {}
        for code, data in data.items():
            if code not in enum_dict:
                enum_dict[code] = data["name"]
        return Enum(enum_name, enum_dict)


class SectorCategoryData(EnumFromCSV):
    """
    See full sectors lists at https://iatistandard.org/en/iati-standard/203/codelists/sector/
    Also, 3 digit version: https://iatistandard.org/en/iati-standard/203/codelists/sectorcategory/
    This codes are a Replicated codelist from OECD Codes
    """
    def __init__(self):
        super().__init__(csv_filename='sector-category-codes.csv', code_field='Code', name_field='Name')


class LocationTypeData(EnumFromCSV):
    def __init__(self):
        super().__init__(csv_filename='location-type-codes.csv', code_field='Code', name_field='Name')
