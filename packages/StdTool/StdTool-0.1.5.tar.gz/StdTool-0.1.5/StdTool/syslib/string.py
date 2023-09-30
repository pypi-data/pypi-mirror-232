import difflib
import mmap
import textwrap
import array
import re
from re import Pattern,RegexFlag
from string import *
from .console import Fore

autoline = textwrap.fill
dedent = textwrap.dedent
indent = textwrap.indent
shorten = textwrap.shorten


def normalize_text(text: str, exlist: str = r'[\s\n\t\r]+') -> str:
    return re.sub(exlist, ' ', text)


def findall(pattern: bytes | Pattern[bytes] | str,
            string: bytes | bytearray | memoryview | array.array | mmap.mmap | str,
            flags: int | RegexFlag = 0,
            error: str = 'remain'
            ) -> list | str:
    import re
    ret = re.findall(pattern, string, flags)
    if not ret:
        if error == 'remain':
            raise ValueError(f'{Fore.LIGHTYELLOW_EX}Pattern Not Find!')
        if error == 'ignore':
            return ['Pattern Not Find!']
        return ['']
    return ret[0] if len(ret) == 1 else ret
