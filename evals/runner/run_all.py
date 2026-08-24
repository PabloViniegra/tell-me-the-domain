#!/usr/bin/env python3
import argparse
import subprocess
import sys
from pathlib import Path

from process_utils import terminate_process
from run_case import validate_case_id


def discover_cases(cases_root: Path, case_ids: list[str] | None = None) -> list[Path]:
    cases_root = cases_root.resolve()
    if not cases_root.is_dir():
        raise ValueError(f"cases root does not exist: {cases_root}")
    cases = sorted(
        path
        for path in cases_root.iterdir()
        if path.is_dir() and not path.is_symlink() and (path / "oracle.json").is_file()
    )
    if not case_ids:
        if not cases:
            raise ValueError(f"no evaluation cases found under {cases_root}")
        return cases
    for case_id in case_ids:
        validate_case_id(case_id)
    requested = {case_id: (cases_root / case_id).resolve() for case_id in case_ids}
    if any(cases_root not in path.parents for path in requested.values()):
        raise ValueError("requested case escaped the cases root")
    missing = [case_id for case_id, path in requested.items() if not (path / "oracle.json").exists()]
    if missing:
        raise ValueError(f"unknown case ids: {', '.join(sorted(missing))}")
    return [requested[case_id] for case_id in case_ids]


def worst_exit_code(exit_codes: list[int]) -> int:
    if not exit_codes:
        return 2
    failures = [code if code > 0 else 1 for code in exit_codes if code != 0]
    return max(failures, default=0)


def run_case_process(command: list[str], timeout: int) -> int:
    try:
        process = subprocess.Popen(command, start_new_session=True)
    except OSError:
        return 2
    try:
        return process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        terminate_process(process)
        return 2


def run_all(
    cases_root: Path,
    output_root: Path,
    agent_cmd: str,
    repeats: int,
    case_ids: list[str] | None = None,
    judge_cmd: str | None = None,
    judge_threshold: float = 0.8,
    agent_timeout: int = 300,
    judge_timeout: int = 120,
    case_timeout: int = 450,
) -> int:
    if not agent_cmd.strip():
        raise ValueError("agent command is empty")
    if not judge_cmd or not judge_cmd.strip():
        raise ValueError("judge command is empty")
    if repeats < 1:
        raise ValueError("repeats must be at least 1")
    if agent_timeout < 1 or judge_timeout < 1:
        raise ValueError("timeouts must be at least 1 second")
    if case_timeout < 1:
        raise ValueError("case timeout must be at least 1 second")
    cases = discover_cases(cases_root, case_ids)
    output_root.mkdir(parents=True, exist_ok=True)
    results = []
    runner = Path(__file__).with_name("run_case.py")

    for repeat in range(1, repeats + 1):
        for case_dir in cases:
            command = [
                sys.executable,
                str(runner),
                "--case",
                str(case_dir),
                "--output-root",
                str(output_root),
                "--agent-cmd",
                agent_cmd,
                "--judge-threshold",
                str(judge_threshold),
                "--agent-timeout",
                str(agent_timeout),
                "--judge-timeout",
                str(judge_timeout),
            ]
            command.extend(["--judge-cmd", judge_cmd])
            print(f"=== {case_dir.name} repeat {repeat}/{repeats} ===")
            result = run_case_process(command, case_timeout)
            results.append((case_dir.name, repeat, result))

    print("--- evaluation summary ---")
    for case_id, repeat, exit_code in results:
        status = "PASS" if exit_code == 0 else "FAIL"
        print(f"{status} {case_id} repeat={repeat} exit={exit_code}")
    worst = worst_exit_code([exit_code for _, _, exit_code in results])
    print(f"worst run exit code: {worst}")
    return worst


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases-root", type=Path, default=Path("evals/cases"))
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--agent-cmd", required=True,
                        help="Shell command to invoke the agent; use {repo} and {output}.")
    parser.add_argument("--judge-cmd", required=True,
                        help="Command that reads the entailment request JSON from stdin")
    parser.add_argument("--judge-threshold", type=float, default=0.8)
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--agent-timeout", type=int, default=300)
    parser.add_argument("--judge-timeout", type=int, default=120)
    parser.add_argument("--case-timeout", type=int, default=450)
    parser.add_argument("--case", dest="case_ids", action="append",
                        help="Run only this case id; may be supplied more than once")
    args = parser.parse_args()

    if args.repeats < 1:
        parser.error("--repeats must be at least 1")
    if not 0 <= args.judge_threshold <= 1:
        parser.error("--judge-threshold must be between 0 and 1")
    if args.agent_timeout < 1 or args.judge_timeout < 1:
        parser.error("timeouts must be at least 1 second")
    if args.case_timeout < 1:
        parser.error("--case-timeout must be at least 1 second")
    try:
        return run_all(
            args.cases_root.resolve(),
            args.output_root.resolve(),
            args.agent_cmd,
            args.repeats,
            case_ids=args.case_ids,
            judge_cmd=args.judge_cmd,
            judge_threshold=args.judge_threshold,
            agent_timeout=args.agent_timeout,
            judge_timeout=args.judge_timeout,
            case_timeout=args.case_timeout,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
