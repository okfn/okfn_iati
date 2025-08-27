import csv
from functools import lru_cache
from typing import Dict, List, Set, Optional

from okfn_iati.data import get_data_folder


class CodelistValidator:
    """
    Base class for IATI codelist validators that load data from CSV files.
    """
    def __init__(self, csv_filename: str, code_column: str = "code"):
        self.csv_filename = csv_filename
        self.code_column = code_column
        self._codes: Optional[Set[str]] = None
        self._data: Optional[List[Dict[str, str]]] = None

    @property
    @lru_cache(maxsize=1)
    def codes(self) -> Set[str]:
        """Get a set of all valid codes."""
        if self._codes is None:
            self._codes = set(row[self.code_column] for row in self.data)
        return self._codes

    @property
    @lru_cache(maxsize=1)
    def data(self) -> List[Dict[str, str]]:
        """Get all codelist data as a list of dictionaries."""
        if self._data is None:
            self._data = self._load_codes()
        return self._data

    def _load_codes(self) -> List[Dict[str, str]]:
        """Load codes from CSV file."""
        data_dir = get_data_folder()
        filepath = data_dir / self.csv_filename
        if not filepath.exists():
            raise Exception(f"File {filepath} not found.")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except FileNotFoundError:
            # Fallback to package resources for installed package
            import importlib.resources as pkg_resources
            from importlib import resources
            from io import StringIO

            try:
                # Python 3.9+
                with resources.files('okfn_iati.data').joinpath(self.csv_filename).open('r') as f:
                    reader = csv.DictReader(f)
                    return list(reader)
            except (ImportError, AttributeError):
                # Python 3.8 and below
                data_text = pkg_resources.read_text('okfn_iati.data', self.csv_filename)
                reader = csv.DictReader(StringIO(data_text))
                return list(reader)

    def is_valid_code(self, code: str) -> bool:
        """Check if a code is valid."""
        return code in self.codes

    def get_by_code(self, code: str) -> Optional[Dict[str, str]]:
        """Get the full data for a specific code."""
        if not code:
            return None

        for item in self.data:
            if item[self.code_column] == code:
                return item
        return None

    def __contains__(self, code: str) -> bool:
        """Enable the 'in' operator for checking if a code is valid."""
        return self.is_valid_code(code)


class CRSChannelCodeValidator(CodelistValidator):
    """Validator for CRS Channel Codes."""

    def __init__(self):
        super().__init__(csv_filename="CRSChannelCode.csv")

    def get_name(self, code: str) -> Optional[str]:
        """Get the name for a specific channel code."""
        data = self.get_by_code(code)
        return data.get('name') if data else None

    def get_category(self, code: str) -> Optional[str]:
        """Get the category for a specific channel code."""
        data = self.get_by_code(code)
        return data.get('category') if data else None


# Create singletons for validators
crs_channel_code_validator = CRSChannelCodeValidator()
