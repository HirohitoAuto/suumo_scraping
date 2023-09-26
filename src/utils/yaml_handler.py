import yaml


def load_yaml(filename: str) -> dict:
    """
    load yaml
    """
    with open(filename, "r") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    return data


def dump_yaml(filename: str, data: dict) -> None:
    """
    dump yaml
    """
    with open(filename, "w") as f:
        yaml.dump(data, f, default_flow_style=False)
    return None
