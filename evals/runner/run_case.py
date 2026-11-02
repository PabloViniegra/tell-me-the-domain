#!/usr/bin/env python3
import argparse
import json
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_outputs as co
from process_utils import terminate_process


CASE_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")


def validate_case_id(case_id: str) -> None:
    if not CASE_ID_RE.fullmatch(case_id):
        raise ValueError(f"invalid case id: {case_id!r}")


def validate_case_tree(case_dir: Path) -> None:
    repo = case_dir / "repo"
    if repo.is_symlink() or not repo.is_dir():
        raise ValueError(f"case repository is missing: {repo}")
    for path in case_dir.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"case contains a symlink: {path}")


SCRATCH_DIR = ".tell-me-the-domain"
CACHE_PATTERNS = ("__pycache__", ".pytest_cache")


def materialize(case_dir: Path, target: Path) -> Path:
    src = case_dir / "repo"
    validate_case_tree(case_dir)
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(src, target, ignore=shutil.ignore_patterns(*CACHE_PATTERNS))
    return target


def snapshot(root: Path, skip) -> dict[str, bytes]:
    entries = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if skip(rel):
            continue
        if path.is_symlink():
            entries[rel.as_posix()] = b"symlink:" + str(path.readlink()).encode()
        elif path.is_dir():
            entries[rel.as_posix() + "/"] = b"dir"
        elif path.is_file():
            entries[rel.as_posix()] = path.read_bytes()
    return entries


def repo_mutations(original: Path, analyzed: Path) -> list[str]:
    before = snapshot(original, lambda rel: any(part in CACHE_PATTERNS for part in rel.parts))
    after = snapshot(analyzed, lambda rel: rel.parts[0] == SCRATCH_DIR)
    changes = [f"added {name}" for name in after.keys() - before.keys()]
    changes += [f"removed {name}" for name in before.keys() - after.keys()]
    changes += [f"modified {name}" for name in before.keys() & after.keys() if before[name] != after[name]]
    return sorted(changes)


DEFAULT_PROMPT = (
    "Use the `tell-me-the-domain` skill to reconstruct the business domain of this repository. "
    "Write BUSINESS_OVERVIEW.md and TECHNICAL_DOMAIN_GUIDE.md into the output directory.\n"
    "Repository: {repo}\nOutput directory: {output}\n"
)


def build_prompt(repo: Path, output: Path, prompt_file: Path | None = None) -> str:
    template = (
        prompt_file.read_text(encoding="utf-8")
        if prompt_file and prompt_file.exists()
        else DEFAULT_PROMPT
    )
    return template.replace("{repo}", str(repo)).replace("{output}", str(output))


def next_run_dir(output_root: Path, case_id: str) -> Path:
    validate_case_id(case_id)
    output_root = output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    case_dir = (output_root / case_id).resolve()
    if output_root not in case_dir.parents:
        raise ValueError(f"case output escaped output root: {case_id!r}")
    case_dir.mkdir(parents=True, exist_ok=True)
    idx = 1
    while (case_dir / f"run-{idx:03d}").exists():
        idx += 1
    run = case_dir / f"run-{idx:03d}"
    run.mkdir()
    return run


def run_agent(
    agent_cmd: str,
    prompt: str,
    repo: Path,
    output: Path,
    timeout: int,
    cwd: Path,
    tmpdir: Path | None = None,
) -> int:
    if not agent_cmd.strip():
        print("agent command is empty", file=sys.stderr)
        return 2
    env = co.evaluation_environment(
        {
            "TMTD_REPO": str(repo),
            "TMTD_OUTPUT_DIR": str(output),
            "TMTD_PROMPT": prompt,
            **({"TMPDIR": str(tmpdir)} if tmpdir else {}),
        }
    )
    rendered = agent_cmd.replace("{repo}", shlex.quote(str(repo))).replace("{output}", shlex.quote(str(output)))
    try:
        proc = subprocess.Popen(
            rendered,
            shell=True,
            env=env,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="replace",
            start_new_session=True,
        )
    except (OSError, ValueError) as exc:
        print(f"agent could not start: {exc}", file=sys.stderr)
        return 2
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        terminate_process(proc)
        print(f"agent timed out after {timeout} seconds", file=sys.stderr)
        return 2
    except (OSError, UnicodeError, ValueError) as exc:
        terminate_process(proc)
        print(f"agent I/O failed: {exc}", file=sys.stderr)
        return 2
    sys.stdout.write(stdout)
    sys.stderr.write(stderr)
    return proc.returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path,
                        help="Directory where a per-case per-run subdirectory will be created")
    parser.add_argument("--agent-cmd", required=True,
                        help="Shell command to invoke the agent. Use {repo} and {output}; the prompt is in $TMTD_PROMPT.")
    parser.add_argument("--judge-cmd",
                        help="Command that reads the entailment request JSON from stdin")
    parser.add_argument("--judge-threshold", type=float, default=0.8)
    parser.add_argument("--agent-timeout", type=int, default=300)
    parser.add_argument("--judge-timeout", type=int, default=120)
    args = parser.parse_args()

    if not 0 <= args.judge_threshold <= 1:
        parser.error("--judge-threshold must be between 0 and 1")
    if args.agent_timeout < 1 or args.judge_timeout < 1:
        parser.error("timeouts must be at least 1 second")

    case_dir = args.case.resolve()
    case_id = case_dir.name
    try:
        validate_case_id(case_id)
        validate_case_tree(case_dir)
        oracle = co.load_oracle(case_dir)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"invalid case: {exc}", file=sys.stderr)
        return 2
    if oracle["case_id"] != case_id:
        print(f"oracle case_id {oracle['case_id']!r} does not match directory {case_id!r}", file=sys.stderr)
        return 2

    try:
        work_dir = next_run_dir(args.output_root, case_id)
    except (OSError, ValueError) as exc:
        print(f"case setup failed: {exc}", file=sys.stderr)
        return 2

    # The case id names the trap under test, so the agent works in a neutrally named sandbox.
    with tempfile.TemporaryDirectory(prefix="tmtd-") as sandbox:
        sandbox = Path(sandbox)
        try:
            repo = materialize(case_dir, sandbox / "repo")
            output = sandbox / "out"
            output.mkdir()
            # Scratch files of the agent command live in the sandbox, so they are removed even after a timeout kill.
            agent_tmp = sandbox / "tmp"
            agent_tmp.mkdir()
            prompt = build_prompt(repo, output, case_dir / "prompt.txt")
            (work_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
        except (OSError, ValueError) as exc:
            print(f"case setup failed: {exc}", file=sys.stderr)
            return 2

        rc = run_agent(args.agent_cmd, prompt, repo, output, args.agent_timeout, Path.cwd(), agent_tmp)
        if rc != 0:
            print(f"agent exited with code {rc}", file=sys.stderr)
            return 2

        try:
            shutil.copytree(output, work_dir, symlinks=True, dirs_exist_ok=True)
            if (repo / SCRATCH_DIR).is_dir():
                shutil.copytree(repo / SCRATCH_DIR, work_dir / SCRATCH_DIR, symlinks=True, dirs_exist_ok=True)
            mutations = repo_mutations(case_dir / "repo", repo)
            if mutations:
                shutil.copytree(repo, work_dir / "analyzed-repo", symlinks=True)
        except OSError as exc:
            print(f"could not collect agent output: {exc}", file=sys.stderr)
            return 2

    rc = co.run_case(
        case_dir,
        work_dir,
        judge_cmd=args.judge_cmd,
        judge_threshold=args.judge_threshold,
        judge_timeout=args.judge_timeout,
    )
    if mutations:
        print("analyzed repository was modified (the skill must not write to or execute product code); "
              f"its final state is in {work_dir / 'analyzed-repo'}:")
        for change in mutations[:20]:
            print(f"  - {change}")
        return max(rc, 1)
    return rc


if __name__ == "__main__":
    sys.exit(main())
