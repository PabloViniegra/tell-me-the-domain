import tempfile
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

    def test_agent_sees_no_case_id_in_prompt_or_paths(self):
        seen = {}

        def fake_agent(agent_cmd, prompt, repo, output, timeout, cwd, tmpdir=None):
            seen.update(prompt=prompt, paths=[str(repo), str(output), str(tmpdir)])
            return 1

        for case_dir in sorted((ROOT / "evals" / "cases").iterdir()):
            with tempfile.TemporaryDirectory() as tmp:
                argv = ["run_case.py", "--case", str(case_dir), "--output-root", tmp, "--agent-cmd", "agent"]
                with patch("sys.argv", argv), patch("run_case.run_agent", side_effect=fake_agent):
                    self.assertEqual(run_case.main(), 2)
            for text in [seen["prompt"], *seen["paths"]]:
                self.assertNotIn(case_dir.name, text)
            self.assertNotIn("{repo}", seen["prompt"])

    def test_case_readmes_do_not_announce_the_fixture(self):
        for readme in (ROOT / "evals" / "cases").glob("*/repo/README.md"):
            text = readme.read_text(encoding="utf-8").lower()
            self.assertNotIn("eval fixture", text, readme)
            self.assertNotIn("the skill must", text, readme)

    def test_repo_mutations_ignore_scratch_ledger_and_preexisting_caches(self):
        with tempfile.TemporaryDirectory() as tmp:
            original = Path(tmp) / "original"
            (original / "__pycache__").mkdir(parents=True)
            (original / "__pycache__" / "a.pyc").write_bytes(b"old")
            (original / "a.py").write_text("x = 1\n")
            analyzed = Path(tmp) / "analyzed"
            run_case.shutil.copytree(original, analyzed, ignore=run_case.shutil.ignore_patterns("__pycache__"))
            (analyzed / ".tell-me-the-domain").mkdir()
            (analyzed / ".tell-me-the-domain" / "notes.md").write_text("ledger")
            self.assertEqual(run_case.repo_mutations(original, analyzed), [])

            (analyzed / "a.py").write_text("x = 2\n")
            (analyzed / "__pycache__").mkdir()
            (analyzed / "__pycache__" / "a.pyc").write_bytes(b"new")
            self.assertEqual(
                run_case.repo_mutations(original, analyzed),
                ["added __pycache__/", "added __pycache__/a.pyc", "modified a.py"],
            )

    def test_repo_mutations_only_exempt_the_root_scratch_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            original = Path(tmp) / "original"
            original.mkdir()
            analyzed = Path(tmp) / "analyzed"
            (analyzed / "docs" / ".tell-me-the-domain").mkdir(parents=True)
            (analyzed / "docs" / ".tell-me-the-domain" / "x.md").write_text("doc")
            (analyzed / "build").mkdir()
            self.assertEqual(
                run_case.repo_mutations(original, analyzed),
                [
                    "added build/",
                    "added docs/",
                    "added docs/.tell-me-the-domain/",
                    "added docs/.tell-me-the-domain/x.md",
                ],
            )

if __name__ == "__main__":
    unittest.main()
