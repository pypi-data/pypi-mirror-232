"""Firepup650's fkeycapture module"""
import termios, fcntl, sys, os
from typing import Union

global fd, flags_save, attrs_save
fd = sys.stdin.fileno()
flags_save = fcntl.fcntl(fd, fcntl.F_GETFL)
attrs_save = termios.tcgetattr(fd)
KEYS = {
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

    fd = sys.stdin.fileno()
    # save old state
    flags_save = fcntl.fcntl(fd, fcntl.F_GETFL)
    attrs_save = termios.tcgetattr(fd)
    # make raw - the way to do this comes from the termios(3) man page.
    attrs = list(attrs_save)  # copy the stored version to update
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
    termios.tcsetattr(fd, termios.TCSANOW, attrs)
    # turn off non-blocking
    fcntl.fcntl(fd, fcntl.F_SETFL, flags_save & ~os.O_NONBLOCK)


def __getp2():
    """Internal Method - Reset terminal settings"""
    termios.tcsetattr(fd, termios.TCSAFLUSH, attrs_save)
    fcntl.fcntl(fd, fcntl.F_SETFL, flags_save)


def __handleDelete(base: list, current: bytes) -> list:
    """Internal Method - Handle deletes"""
    if current == KEYS["BACKSPACE"]:
        base.pop()
    else:
        base.append(current.decode())
    return base


def get(
    keycount: int = 1, bytes: bool = False, allowDelete: bool = False, osReader=False
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
    keys = []
    while internalcounter != keycount:
        if osReader:
            key = os.read(fd, 6)
        else:
            key = sys.stdin.read(1)
        if allowDelete:
            keys = __handleDelete(keys, key)
        else:
            keys.append(key.decode())
        internalcounter = len(keys)
    key = "".join(keys)  # type: ignore[arg-type]
    __getp2()
    if bytes:
        return key.encode()
    else:
        return key


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
    keys = []
    while internalcounter != keycount:
        key = get()
        if key in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            if allowDelete:
                keys = __handleDelete(keys, key.encode())
            else:
                keys.append(key)
            internalcounter = len(keys)
    key = "".join(keys)  # type: ignore[arg-type]
    if not ints:
        return key
    else:
        return int(key)


def getchars(
    keycount: int = 1,
    chars: list = ["1", "2"],
    bytes: bool = False,
    allowDelete: bool = False,
) -> Union[str, bytes]:
    """# Function: getchars

    # Inputs:
      keycount: int     - Number of keys, defualts to 1
      chars: list       - List of allowed keys, defaults to ["1", "2"]
      bytes: bool       - Wether or not to return the key(s) as bytes, defaults to False
      allowDelete: bool - Wether to allow deleting chars, defaults to False

    # Returns:
      Union[str, bytes]

    # Raises:
      None"""
    internalcounter = 0
    keys = []
    while internalcounter != keycount:
        key = get()
        if key in chars:
            if allowDelete:
                keys = __handleDelete(keys, key.encode())
            else:
                keys.append(key)
            internalcounter = len(keys)
    key = "".join(keys)  # type: ignore[arg-type]
    if not bytes:
        return key
    else:
        return key.encode()
