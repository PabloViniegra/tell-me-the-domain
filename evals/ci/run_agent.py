#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path


REQUIRED = ("TMTD_PROMPT", "TMTD_REPO", "TMTD_OUTPUT_DIR")


def skill_root() -> Path:
    return Path(__file__).resolve().parents[2]


def build_command() -> list[str]:
    missing = [name for name in REQUIRED if not os.environ.get(name, "").strip()]
    if missing:
        raise ValueError(f"missing environment: {', '.join(missing)}")

    prompt = os.environ["TMTD_PROMPT"]
    repo = os.environ["TMTD_REPO"]
    output = os.environ["TMTD_OUTPUT_DIR"]
    model = os.environ.get("TMTD_AGENT_MODEL", "").strip()
    message = (
        f"{prompt}\n"
        "Write English documents unless the prompt already chose another language.\n"
        "Write BUSINESS_OVERVIEW.md and TECHNICAL_DOMAIN_GUIDE.md into the output directory. "
        "Do not wait for a second language confirmation.\n"
        "Every document must state the analysis mode in a header blockquote "
        "(complete context or repository atlas) and a date or commit. "
        "Replace every template placeholder, including the product name. "
        "The technical guide must contain a '## Coverage matrix' section with recognized statuses.\n"
        f"Skill repository: {skill_root()}\n"
        f"Case repository: {repo}\n"
        f"Output directory: {output}\n"
    )
    command = [
        "opencode",
        "run",
        "--auto",
        "--dir",
        str(skill_root()),
        "--title",
        "tmtd-eval-agent",
        message,
    ]
    if model:
        command[3:3] = ["--model", model]
    return command


def main() -> int:
    try:
        command = build_command()
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    try:
        proc = subprocess.run(command, check=False)
    except OSError as exc:
        print(f"agent could not start: {exc}", file=sys.stderr)
        return 2
    return 0 if proc.returncode == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
