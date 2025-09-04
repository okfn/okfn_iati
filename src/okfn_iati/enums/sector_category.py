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

        # 1) usar utf-8-sig para comer el BOM si aparece
        with open(self.csv_path, encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)

            # 2) Normalizar nombres de columnas (por si queda algún BOM o espacios)
            if reader.fieldnames:
                reader.fieldnames = [fn.strip().lstrip("\ufeff") for fn in reader.fieldnames]

            for row in reader:
                # 3) Normalizar claves del row
                norm_row = {k.strip().lstrip("\ufeff"): (v.strip() if isinstance(v, str) else v)
                            for k, v in row.items() if k is not None}

                code = norm_row[self.code_field]  # ahora sí existe 'Code'
                self.data[code] = {"name": norm_row[self.name_field]}

                # Copiar el resto de las columnas (si las hay)
                for key, value in norm_row.items():
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
    def __init__(self):
        super().__init__(csv_filename='sector-category-codes.csv', code_field='Code', name_field='Name')


class LocationTypeData(EnumFromCSV):
    def __init__(self):
        super().__init__(csv_filename='location-type-codes.csv', code_field='Code', name_field='Name')

    @classmethod
    def to_enum(cls, enum_name="LocationType"):
        """Genera un Enum con nombres normalizados a partir del CSV."""
        data = cls().load_data()
        members = {}
        for code, row in data.items():
            # row["name"] viene del CSV (columna Name)
            member_name = _normalize_enum_name(row["name"])
            # Evitar colisiones: nos quedamos con el primer match (el CSV ya es único por Name útil)
            if member_name not in members:
                members[member_name] = code  # valor del enum = código IATI (p.ej., 'PPL')
        return Enum(enum_name, members)


def _normalize_enum_name(s: str) -> str:
    # MAYÚSCULAS y reemplazar cualquier cosa no alfanumérica por "_"
    return re.sub(r'[^A-Z0-9]+', '_', s.upper()).strip('_')
