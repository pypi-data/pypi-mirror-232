import subprocess
import asyncio.subprocess
from functools import partial
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

run_block = subprocess.run
Popen = subprocess.Popen


async def run_async(cmd: str, sem: asyncio.Semaphore = None, in_time_output=False):
    if sem:
        async with sem:
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE)

            stdout, stderr = await proc.communicate()
            if in_time_output:
                print(time.ctime(), cmd, stdout)
            return stdout
    else:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

        stdout, stderr = await proc.communicate()
        if in_time_output:
            print(time.ctime(), cmd, stdout)
        return stdout


async def run_async_maps(cmds, process=4, in_time_output=False):
    sem = asyncio.Semaphore(process)
    return await asyncio.gather(
        *map(partial(run_async, sem=sem, in_time_output=in_time_output), cmds))


def run_concurrent_async(cmds: list[str], process=4, in_time_output=False):
    return asyncio.run(run_async_maps(cmds, process, in_time_output))


def run_concurrent_thread(cmds: list[str], process=4, in_time_output=False):
    ret = {}
    with ThreadPoolExecutor(max_workers=process) as pool:
        futures = {
            pool.submit(subprocess.run, cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf8'): cmd
            for cmd in
            cmds}
        for future in as_completed(futures):
            out = future.result().stdout
            ret[futures[future]] = out
            if in_time_output:
                print(time.ctime(), futures[future], ' : ', out)
    return ret


