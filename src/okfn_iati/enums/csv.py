import csv
from okfn_iati.data import get_data_folder


class CodeNameFieldFromCSV:
    """ A large field from CSV. We expect at least a unique code and a Name """
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
        return self.data[code]

    def get(self, code):
        if not self._loaded:
            self.load_data()
        return self.data.get(code)

    def values(self):
        if not self._loaded:
            self.load_data()
        return self.data.values()

    def items(self):
        if not self._loaded:
            self.load_data()
        return self.data.items()

    def __repr__(self):
        if not self._loaded:
            self.load_data()
        return f"{self.__class__.__name__}({dict(self.data)})"

    def __str__(self):
        return self.__repr__()

    def __contains__(self, code):
        if not self._loaded:
            self.load_data()
        return code in self.data

    def __len__(self):
        if not self._loaded:
            self.load_data()
        return len(self.data)

    def __iter__(self):
        if not self._loaded:
            self.load_data()
        return iter(self.data.values())

    def keys(self):
        if not self._loaded:
            self.load_data()
        return self.data.keys()


class SectorCategoryData(CodeNameFieldFromCSV):
    def __init__(self):
        super().__init__(csv_filename='sector-category-codes.csv', code_field='Code', name_field='Name')


class CRSChannelCodesData(CodeNameFieldFromCSV):
    def __init__(self):
        super().__init__(csv_filename='crs-channel-codes.csv')
