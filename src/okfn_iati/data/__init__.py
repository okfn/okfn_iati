from pathlib import Path


def get_data_folder() -> Path:
    """ For this library to get access to data files """
    return Path(__file__).parent
