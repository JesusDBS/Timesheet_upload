import json
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
    

def report_done(fun: Callable) -> Callable:
    """Reports when a function has been executed
    """
    def wrapper(*args, **kwagrs):
        fun(*args, **kwagrs)
        print(f".........{fun.__name__} is done.........")
    return wrapper
