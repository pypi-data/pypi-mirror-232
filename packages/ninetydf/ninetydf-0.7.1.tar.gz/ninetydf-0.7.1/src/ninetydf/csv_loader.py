from dataclasses import fields
from typing import List, Type, Union

from .models import Couple, Season


def _load_data(
    filename: str, dataclass: Type[Union[Couple, Season]]
) -> List[Union[Couple, Season]]:
    data_list = []

    # Create a mapping from field names to their types
    type_mapping = {f.name: f.type for f in fields(dataclass)}

    try:
        from importlib.resources import files  # Standard Python 3.9+
    except ImportError:
        from importlib_resources import files

    resource_path = files("ninetydf") / filename
    with resource_path.open(encoding="utf-8") as f:
        header = f.readline().strip().split(",")
        for line in f:
            row = line.strip().split(",")

            for i, column in enumerate(header):
                if column in type_mapping:
                    if type_mapping[column] == int:
                        row[i] = int(row[i])

            instance = dataclass(*row)
            data_list.append(instance)

    return data_list


def load_couples() -> List[Couple]:
    return _load_data("couples.csv", Couple)


def load_seasons() -> List[Season]:
    return _load_data("seasons.csv", Season)
