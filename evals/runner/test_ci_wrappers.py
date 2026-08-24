import io
import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ci"))

import run_agent
import run_judge


class AgentWrapperTests(unittest.TestCase):
    def test_missing_env_is_infrastructure_failure(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(run_agent.main(), 2)

    def test_builds_opencode_command_against_the_skill_repo(self):
        env = {
            "TMTD_PROMPT": "Document this.",
            "TMTD_REPO": "/tmp/case-repo",
            "TMTD_OUTPUT_DIR": "/tmp/case-out",
        }
        with patch.dict(os.environ, env, clear=True):
            command = run_agent.build_command()

        joined = " ".join(command)
        self.assertEqual(command[0], "opencode")
        self.assertIn("run", command)
        self.assertIn("--auto", command)
        self.assertIn("/tmp/case-repo", joined)
        self.assertIn("/tmp/case-out", joined)


class JudgeWrapperTests(unittest.TestCase):
    def test_empty_stdin_is_infrastructure_failure(self):
        with patch("sys.stdin", io.StringIO("")):
            self.assertEqual(run_judge.main(), 2)

    def test_extracts_one_result_per_fact_from_model_text(self):
        request = {
            "facts": [
                {"id": "R-001", "statement": "A rule holds."},
                {"id": "C-001", "statement": "A concept exists."},
            ]
        }
        payload = {
            "facts": [
                {"id": "R-001", "entailed": True, "score": 0.9, "reason": "stated"},
                {"id": "C-001", "entailed": False, "score": 0.2, "reason": "missing"},
            ]
        }
        text = "Here you go:\n```json\n" + json.dumps(payload) + "\n```\n"

        result = run_judge.parse_judge_output(text, {"R-001", "C-001"})

        self.assertTrue(result["facts"][0]["entailed"])
        self.assertEqual(result["facts"][1]["id"], "C-001")

        with self.assertRaises(ValueError):
            run_judge.parse_judge_output("not json", {"R-001"})


if __name__ == "__main__":
    unittest.main()
