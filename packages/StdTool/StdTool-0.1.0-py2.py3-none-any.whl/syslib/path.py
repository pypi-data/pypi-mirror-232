from pathlib import Path
import shutil
import os as _os


def cp(src, dst, exist_ok=True):
    if Path(src).is_dir():
        return shutil.copytree(src, dst, dirs_exist_ok=exist_ok)
    else:
        return shutil.copy(src, dst)


def mv(src, dst):
    return shutil.move(src, dst)


def rm(src):
    return shutil.rmtree(src)


def mkdir(src, remake=False):
    p = Path(src)
    if remake and p.exists():
        p.rmdir()
    return p.mkdir(exist_ok=True)


def rename(src, dst):
    p = Path(src)
    return p.rename(dst)


def ln(src, dst):
    src = Path(src)
    if src.exists():
        return _os.symlink(src, dst, target_is_directory=src.is_dir())
    raise FileNotFoundError(f"Not Valid path {src} !")


def ls(dst):
    print(*Path(dst).iterdir())


def map_dir(func, dst, pattern='*'):
    dst = Path(dst)
    return [func(i) for i in dst.rglob(pattern)]



chmod = _os.chmod
try:
    chown = _os.chown
except AttributeError:
    pass
du = disk_usage = shutil.disk_usage
which = shutil.which
md = mkdir
rn = rename
