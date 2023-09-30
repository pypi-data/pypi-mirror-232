from . import path, time, console, envs, string
import sys as _sys
from pathlib import Path
import os as _os
if _sys.platform == "win32":
    import winreg

os_name = _sys.platform
imp = _sys.implementation
interpreter = _sys.executable
PATH = _sys.path
version = _sys.version_info
package_path = Path(__file__).parent.parent
stdin = _sys.stdin
stdout = _sys.stdout
stderr = _sys.stderr
StdTool = _sys.modules["StdTool"]
syslib = _sys.modules[__name__]
#
# cpu_cores = _os.cpu_count()
# username = _os.getlogin()
# print(__path__)
