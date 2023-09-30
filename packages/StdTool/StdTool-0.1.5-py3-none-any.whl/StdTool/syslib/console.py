import builtins
import contextlib
import sys
from pprint import pprint, pformat

CSI = '\033['
OSC = '\033]'
BEL = '\a'


def print(*args, color: str | None = None, seq=' ', file=sys.stdout, end='\n', flush=False, **kwargs):
    prefix, subfix = '', ''
    values = (pformat(value, indent=2, depth=2) if not isinstance(value, str) else value for value in args)
    if color:
        prefix = getattr(Fore, color.upper())
        subfix = str(Fore.RESET)
    file.write(prefix + seq.join(values) + subfix + end)
    if flush:
        file.flush()


builtins.print = print


@contextlib.contextmanager
def hight_light(color='YELLOW', **kwargs):
    import builtins

    try:
        c = getattr(Fore, color.upper())
        print(c, end='')
    except Exception as e:
        print(e)
    yield lambda *args, **kwargs: print(Fore.RESET, end='') or print(*args, **kwargs) or print(c, end='')
    print(Fore.RESET, end='')


@contextlib.contextmanager
def redirect(*, infile=None, outfile=None, errorfile=None):
    assert infile or outfile or errorfile, "文件不存在！"
    if infile:
        infile = infile
        std_in = sys.stdin
        sys.stdin = infile
    if outfile:
        outfile = outfile
        print(id(sys.stdout))
        std_out = sys.stdout
        sys.stdout = outfile
    if errorfile:
        errorfile = errorfile
        std_error = sys.stderr
        sys.stderr = errorfile
    yield
    if infile:
        sys.stdin = std_in
        infile.close()
    if outfile:
        sys.stdout = std_out
        outfile.close()
    if errorfile:
        errorfile.close()
        sys.stderr = std_error


def tqdm(iter_=None, *, desc='process', total=None, postfix=None, **kwargs):
    from tqdm import tqdm as tq
    bar = tq(
        iterable=iter_,
        ncols=100,
        file=sys.stdout,
        bar_format=f'{Fore.LIGHTBLUE_EX}{{desc}}{Fore.LIGHTWHITE_EX}:{Fore.LIGHTRED_EX}{{percentage:3.0f}}%{Fore.LIGHTGREEN_EX}|{{bar}}| {Fore.LIGHTYELLOW_EX}{{n_fmt}}/{{total_fmt}} [{Fore.LIGHTMAGENTA_EX}{{elapsed}}<{{remaining}}{Fore.LIGHTYELLOW_EX}, {{rate_fmt}}{{postfix}}]{Fore.RESET}',
        desc=desc,
        total=total,
        postfix=postfix,
        position=0,
        nrows=4,
        smoothing = 0.6,
        **kwargs
    )
    f = print
    en = tq.__enter__
    ex = tq.__exit__

    def enter(self):
        nonlocal f
        builtins.print = lambda *x, **kwargs: self.write(kwargs.get('seq', ' ').join(map(str, x)), file=sys.stdout)
        return self

    def exit_(self, *args):
        nonlocal f
        builtins.print = f
        return ex(self, *args)

    setattr(bar.__class__, '__enter__', enter)
    setattr(bar.__class__, '__exit__', exit_)
    return bar


def code_to_chars(code):
    return CSI + str(code) + 'm'


def set_title(title):
    return OSC + '2;' + title + BEL


def clear_screen(mode=2):
    return CSI + str(mode) + 'J'


def clear_line(mode=2):
    return CSI + str(mode) + 'K'


class AnsiCodes(object):
    def __init__(self):
        # the subclasses declare class attributes which are numbers.
        # Upon instantiation we define instance attributes, which are the same
        # as the class attributes but wrapped with the ANSI escape sequence
        for name in dir(self):
            if not name.startswith('_'):
                value = getattr(self, name)
                setattr(self, name, code_to_chars(value))


class AnsiCursor(object):
    def UP(self, n=1):
        return CSI + str(n) + 'A'

    def DOWN(self, n=1):
        return CSI + str(n) + 'B'

    def FORWARD(self, n=1):
        return CSI + str(n) + 'C'

    def BACK(self, n=1):
        return CSI + str(n) + 'D'

    def POS(self, x=1, y=1):
        return CSI + str(y) + ';' + str(x) + 'H'


class AnsiFore(AnsiCodes):
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37
    RESET = 39

    # These are fairly well supported, but not part of the standard.
    LIGHTBLACK_EX = 90
    LIGHTRED_EX = 91
    LIGHTGREEN_EX = 92
    LIGHTYELLOW_EX = 93
    LIGHTBLUE_EX = 94
    LIGHTMAGENTA_EX = 95
    LIGHTCYAN_EX = 96
    LIGHTWHITE_EX = 97


class AnsiBack(AnsiCodes):
    BLACK = 40
    RED = 41
    GREEN = 42
    YELLOW = 43
    BLUE = 44
    MAGENTA = 45
    CYAN = 46
    WHITE = 47
    RESET = 49

    # These are fairly well supported, but not part of the standard.
    LIGHTBLACK_EX = 100
    LIGHTRED_EX = 101
    LIGHTGREEN_EX = 102
    LIGHTYELLOW_EX = 103
    LIGHTBLUE_EX = 104
    LIGHTMAGENTA_EX = 105
    LIGHTCYAN_EX = 106
    LIGHTWHITE_EX = 107


class AnsiStyle(AnsiCodes):
    BRIGHT = 1
    DIM = 2
    NORMAL = 22
    RESET_ALL = 0


Fore = AnsiFore()
Back = AnsiBack()
Style = AnsiStyle()
Cursor = AnsiCursor()
