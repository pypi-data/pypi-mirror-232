import pip as _pip
import warnings
from io import StringIO
from .console import redirect

warnings.filterwarnings('ignore')


def set_source(source='https://pypi.tuna.tsinghua.edu.cn/simple'):
    return _pip.main(['config', 'set', 'global.index-url', source])


def make_env(rq="requirements.txt"):
    return _pip.main(['install', '-r', rq])


def install(package):
    return _pip.main(['install', package])


def uninstall(package):
    return _pip.main(['uninstall', '-y', package])


def list():
    output = StringIO()
    with redirect(outfile=output, errorfile=output):
        _pip.main(['list'])
        raw = output.getvalue().split('\n')
        return {i.split()[0]: i.split()[1] for i in raw[5:] if i}


if __name__ == '__main__':
    print(list())
