"""Firepup650's fkeycapture module"""
import termios, fcntl, sys, os
from typing import Union, Iterable, Any

global _fd, _flags_save, _attrs_save
_fd: int = sys.stdin.fileno()
_flags_save: int = fcntl.fcntl(_fd, fcntl.F_GETFL)
_attrs_save: list[Any] = termios.tcgetattr(_fd)
KEYS: dict = {
    # Arrow Keys
    "UP": b"\x1b[A",
    "DOWN": b"\x1b[B",
    "RIGHT": b"\x1b[C",
    "LEFT": b"\x1b[D",
    # Kill Keys
    "CTRL_C": b"\x03",
    "CTRL_D": b"\x04",
    # F Keys
    "F1": b"\x1bOP",
    "F2": b"\x1bOQ",
    "F3": b"\x1bOR",
    "F4": b"\x1bOS",
    "F5": b"\x1b[15~",
    "F6": b"\x1b[17~",
    "F7": b"\x1b[18~",
    "F8": b"\x1b[19~",
    "F9": b"\x1b[20~",
    "F10": b"\x1b[21~",
    "F11": b"\x1b[23~",
    "F12": b"\x1b[24~",
    # Misc Keys
    "BACKSPACE": b"\x7f",
    "INS": b"\x1b[2~",
    "DEL": b"\x1b[3~",
    "END": b"\x1b[F",
    "HM": b"\x1b[H",
    "PAGE_UP": b"\x1b[5~",
    "PAGE_DOWN": b"\x1b[6~",
    "TAB": b"\t",
    "ENTER": b"\r",
}


def __getp1():
    """Internal Method - Modify terminal settings"""

    _fd = sys.stdin.fileno()
    # save old state
    flags_save = fcntl.fcntl(_fd, fcntl.F_GETFL)
    _attrs_save = termios.tcgetattr(_fd)
    # make raw - the way to do this comes from the termios(3) man page.
    attrs = list(_attrs_save)  # copy the stored version to update
    # iflag
    attrs[0] &= ~(
        termios.IGNBRK
        | termios.BRKINT
        | termios.PARMRK
        | termios.ISTRIP
        | termios.INLCR
        | termios.IGNCR
        | termios.ICRNL
        | termios.IXON
    )
    # oflag
    attrs[1] &= ~termios.OPOST
    # cflag
    attrs[2] &= ~(termios.CSIZE | termios.PARENB)
    attrs[2] |= termios.CS8
    # lflag
    attrs[3] &= ~(
        termios.ECHONL | termios.ECHO | termios.ICANON | termios.ISIG | termios.IEXTEN
    )
    termios.tcsetattr(_fd, termios.TCSANOW, attrs)
    # turn off non-blocking
    fcntl.fcntl(_fd, fcntl.F_SETFL, flags_save & ~os.O_NONBLOCK)


def __getp2():
    """Internal Method - Reset terminal settings"""
    termios.tcsetattr(_fd, termios.TCSAFLUSH, _attrs_save)
    fcntl.fcntl(_fd, fcntl.F_SETFL, _flags_save)


def __handleDelete(base: list[str], current: bytes) -> list[str]:
    """Internal Method - Handle deletes"""
    if current == KEYS["BACKSPACE"]:
        base.pop()
    else:
        base.append(current.decode())
    return base


def get(
    keycount: int = 1,
    bytes: bool = False,
    allowDelete: bool = False,
    osReader: bool = False,
) -> Union[str, bytes]:
    """# Function: get

    # Inputs:
      keycount: int     - Number of keys, defualts to 1
      bytes: bool       - Wether to return the key(s) as bytes, defaults to False
      allowDelete: bool - Wether to allow deleting chars, defaults to False
      osReader: bool - Wether to use os.read, defaults to False

    # Returns:
      Union[str, bytes]

    # Raises:
      None"""
    __getp1()
    internalcounter = 0
    keys: list[str] = []
    while internalcounter != keycount:
        if osReader:
            key = os.read(_fd, 6)
        else:
            key = sys.stdin.read(1).encode()
        if allowDelete:
            keys = __handleDelete(keys, key)
        else:
            keys.append(key.decode())
        internalcounter = len(keys)
    out = "".join(keys)  # type: str
    __getp2()
    if bytes:
        return out.encode()
    else:
        return out


def getnum(
    keycount: int = 1, ints: bool = False, allowDelete: bool = False
) -> Union[str, int]:
    """# Function: getnum

    # Inputs:
      keycount: int     - Number of keys, defualts to 1
      ints: bool        - Wether to return the keys as ints, defaults to False
      allowDelete: bool - Wether to allow deleting chars, defaults to False

    # Returns:
      Union[str, int]

    # Raises:
      None"""
    internalcounter = 0
    keys: list[str] = []
    while internalcounter != keycount:
        key = get()  # type: str#type: ignore
        if key in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            if allowDelete:
                keys = __handleDelete(keys, key.encode())
            else:
                keys.append(key)
            internalcounter = len(keys)
    out = "".join(keys)
    if not ints:
        return out
    else:
        return int(out)


def getchars(
    keycount: int = 1,
    chars: Iterable[str] = ["1", "2"],
    bytes: bool = False,
    allowDelete: bool = False,
) -> Union[str, bytes]:
    """# Function: getchars

    # Inputs:
      keycount: int        - Number of keys, defualts to 1
      chars: Iterable[str] - Iterable of allowed keys, defaults to ["1", "2"]
      bytes: bool          - Wether or not to return the key(s) as bytes, defaults to False
      allowDelete: bool    - Wether to allow deleting chars, defaults to False

    # Returns:
      Union[str, bytes]

    # Raises:
      None"""
    internalcounter = 0
    keys: list[str] = []
    while internalcounter != keycount:
        key = get()  # type: str#type: ignore
        if key in chars:
            if allowDelete:
                keys = __handleDelete(keys, key.encode())
            else:
                keys.append(key)
            internalcounter = len(keys)
    out = "".join(keys)
    if not bytes:
        return out
    else:
        return out.encode()
