import json


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
