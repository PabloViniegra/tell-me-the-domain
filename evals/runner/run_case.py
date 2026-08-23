#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_outputs as co


def materialize(case_dir: Path, target: Path) -> Path:
    src = case_dir / "repo"
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(src, target)
    return target


def build_prompt(case_id: str, repo: Path, output: Path) -> str:
    focus_by_case = {
        "S01-single-context": "Focus on the claim service end to end.",
        "S02-rule-in-fixture": "The fee percentage lives in configuration and the golden fixture; capture it from there.",
        "S03-contradictory-layers": "Document the 30-day and 14-day versions as a conflict, not as a chosen rule.",
        "S04-async-events-only": "The lifecycle is encoded in past-tense events; there is no status column.",
        "S05-multi-tenant-scoping": "Tenant isolation lives in the WHERE clause; flag the unsafe variant.",
        "S06-cross-context-bus": "Two contexts share events implicitly; document both ends of the bus.",
    }
    focus = focus_by_case.get(case_id, "")
    return (
        "Use the `tell-me-the-domain` skill to reconstruct the business domain of this repository. "
        "Write BUSINESS_OVERVIEW.md and TECHNICAL_DOMAIN_GUIDE.md into the output directory.\n"
        f"Repository: {repo}\nOutput directory: {output}\n{focus}"
    )


def next_run_dir(output_root: Path, case_id: str) -> Path:
    case_dir = output_root / case_id
    case_dir.mkdir(parents=True, exist_ok=True)
    idx = 1
    while (case_dir / f"run-{idx:03d}").exists():
        idx += 1
    run = case_dir / f"run-{idx:03d}"
    run.mkdir()
    return run


def run_agent(agent_cmd: str, prompt: str, repo: Path, output: Path) -> int:
    env = os.environ.copy()
    env["TMTD_REPO"] = str(repo)
    env["TMTD_OUTPUT_DIR"] = str(output)
    env["TMTD_PROMPT"] = prompt
    rendered = agent_cmd.replace("{repo}", str(repo)).replace("{output}", str(output))
    proc = subprocess.run(rendered, shell=True, env=env, capture_output=True, text=True)
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    return proc.returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path,
                        help="Directory where a per-case per-run subdirectory will be created")
    parser.add_argument("--agent-cmd", required=True,
                        help="Shell command to invoke the agent. Use {repo} and {output}; the prompt is in $TMTD_PROMPT.")
    args = parser.parse_args()

    case_dir = args.case.resolve()
    oracle = json.loads((case_dir / "oracle.json").read_text())
    case_id = oracle["case_id"]

    work_dir = next_run_dir(args.output_root, case_id)
    repo = materialize(case_dir, work_dir / "repo")
    prompt = build_prompt(case_id, repo, work_dir)
    (work_dir / "prompt.txt").write_text(prompt)

    rc = run_agent(args.agent_cmd, prompt, repo, work_dir)
    if rc != 0:
        print(f"agent exited with code {rc}", file=sys.stderr)
        return 2

    return co.run_case(case_dir, work_dir)


if __name__ == "__main__":
    sys.exit(main())
