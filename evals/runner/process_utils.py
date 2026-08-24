import os
import signal
import subprocess
from pathlib import Path


def _children(pid: int) -> list[int]:
    try:
        raw = (Path(f"/proc/{pid}/task/{pid}/children")).read_text()
    except (FileNotFoundError, OSError):
        return []
    return [int(value) for value in raw.split()]


def terminate_process_tree(pid: int, process_group_id: int | None = None) -> None:
    if process_group_id is None:
        try:
            process_group_id = os.getpgid(pid)
        except ProcessLookupError:
            process_group_id = None
    pending = [pid]
    descendants = []
    while pending:
        current = pending.pop()
        children = _children(current)
        descendants.extend(children)
        pending.extend(children)

    for descendant in reversed(descendants):
        try:
            os.kill(descendant, signal.SIGKILL)
        except ProcessLookupError:
            pass
    if process_group_id is not None:
        try:
            os.killpg(process_group_id, signal.SIGKILL)
        except ProcessLookupError:
            pass
    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def terminate_process(process: subprocess.Popen) -> None:
    terminate_process_tree(process.pid, process.pid)
    for stream in (process.stdin, process.stdout, process.stderr):
        if stream is not None:
            stream.close()
    try:
        process.wait(timeout=1)
    except subprocess.TimeoutExpired:
        try:
            process.kill()
        except ProcessLookupError:
            pass
        process.wait()
