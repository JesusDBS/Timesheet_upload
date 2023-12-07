import json
import re
import datetime
from typing import Callable


def parse_config(path: str = 'config.json') -> dict:
    """Parses config json to Python dict
    """
    assert isinstance(path, str), f'Jason path: {path} must be a string!'

    try:

        with open(path, "r") as j:
            config_json = json.load(j)

        return config_json

    except:

        raise FileNotFoundError("Json file not found")
    

def update_date_in_filename(path: str, format: str = "%Y-%m-%d") -> str:
    """Updates the current date in the filename
    """
    date = datetime.datetime.today().strftime(format)

    path = re.split(r'\d+', path)
    path = [path[0], f'{date}_{date}', path[-1]]

    return ''.join(path)


def report_done(fun: Callable) -> Callable:
    """Reports when a function has been executed
    """
    def wrapper(*args, **kwagrs):
        fun(*args, **kwagrs)
        print(f".........{fun.__name__} is done.........")
    return wrapper
