import unittest
from pathlib import Path
from unittest.mock import patch

import run_all
import run_case


ROOT = Path(__file__).resolve().parents[2]


class RunAllTests(unittest.TestCase):
    def test_worst_exit_code_is_used_instead_of_an_average(self):
        self.assertEqual(run_all.worst_exit_code([0, 1, 0]), 1)
        self.assertEqual(run_all.worst_exit_code([0, 2, 1]), 2)
        self.assertEqual(run_all.worst_exit_code([0, -9]), 1)
        self.assertEqual(run_all.worst_exit_code([0, 0]), 0)
        self.assertEqual(run_all.worst_exit_code([]), 2)

    def test_empty_case_directory_is_rejected(self):
        with self.assertRaises(ValueError):
            run_all.run_all(
                ROOT / "does-not-exist",
                Path("/tmp/tmtd-test-output"),
                "agent",
                1,
                judge_cmd="judge",
            )

    def test_blank_judge_command_is_rejected_before_discovery(self):
        with self.assertRaises(ValueError):
            run_all.run_all(
                ROOT / "evals" / "cases",
                Path("/tmp/tmtd-test-output"),
                "agent",
                1,
                judge_cmd=" ",
            )

    def test_all_successful_cases_return_zero(self):
        with patch("run_all.run_case_process", return_value=0):
            result = run_all.run_all(
                ROOT / "evals" / "cases",
                Path("/tmp/tmtd-test-output"),
                "agent",
                1,
                case_ids=["S08-empty-repo"],
                judge_cmd="judge",
            )

        self.assertEqual(result, 0)

    def test_case_prompt_overrides_default_wording_and_expands_paths(self):
        case_dir = ROOT / "evals" / "cases" / "S07-disabled-feature-flag"
        prompt = run_case.build_prompt(
            "S07-disabled-feature-flag",
            Path("/tmp/run/repo"),
            Path("/tmp/run"),
            case_dir / "prompt.txt",
        )

        self.assertIn("/tmp/run/repo", prompt)
        self.assertIn("disabled automatic renewal discount", prompt)
        self.assertNotIn("{repo}", prompt)


if __name__ == "__main__":
    unittest.main()
