from typing import Iterable, Union

KEYS: dict

def get(
    keycount: int = ...,
    bytes: bool = ...,
    allowDelete: bool = ...,
    osReader: bool = ...,
) -> Union[str, bytes]: ...
def getnum(
    keycount: int = ..., ints: bool = ..., allowDelete: bool = ...
) -> Union[str, int]: ...
def getchars(
    keycount: int = ...,
    chars: Iterable[str] = ...,
    bytes: bool = ...,
    allowDelete: bool = ...,
) -> Union[str, bytes]: ...
