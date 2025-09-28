from typing import NamedTuple


class Signal(NamedTuple):
    name: str
    sender: str
    receiver: str
    file: str
