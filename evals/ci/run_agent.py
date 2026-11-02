#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


REQUIRED = ("TMTD_PROMPT", "TMTD_REPO", "TMTD_OUTPUT_DIR")
DEFAULT_MODEL = "opencode/deepseek-v4.1-flash-free"


def skill_source() -> Path:
    override = os.environ.get("TMTD_SKILL_DIR", "").strip()
    if override:
        return Path(override).resolve()
    return Path(__file__).resolve().parents[2] / "skills" / "tell-me-the-domain"


def build_command(skill_dir: Path) -> list[str]:
    missing = [name for name in REQUIRED if not os.environ.get(name, "").strip()]
    if missing:
        raise ValueError(f"missing environment: {', '.join(missing)}")

    prompt = os.environ["TMTD_PROMPT"]
    repo = os.environ["TMTD_REPO"]
    output = os.environ["TMTD_OUTPUT_DIR"]
    model = os.environ.get("TMTD_AGENT_MODEL", "").strip() or DEFAULT_MODEL
    # Installed copies of the skill may be stale, so point the agent at the candidate explicitly.
    message = (
        f"{prompt}\n"
        f"The skill under test lives in {skill_dir}. Read {skill_dir / 'SKILL.md'} and follow it; "
        "it overrides any installed skill with the same name.\n"
        "Answer to the skill's language question, given in advance: English.\n"
        f"Repository to analyze (current directory): {repo}\n"
        f"Write the deliverables into: {output}\n"
    )
    return ["opencode", "run", "--auto", "--model", model, "--title", "tmtd-eval-agent", message]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="tmtd-skill-") as tmp:
        skill_dir = Path(tmp) / "tell-me-the-domain"
        try:
            command = build_command(skill_dir)
            shutil.copytree(skill_source(), skill_dir)
        except (OSError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return 2
        try:
            proc = subprocess.run(command, cwd=os.environ["TMTD_REPO"], check=False)
        except OSError as exc:
            print(f"agent could not start: {exc}", file=sys.stderr)
            return 2
    return 0 if proc.returncode == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
