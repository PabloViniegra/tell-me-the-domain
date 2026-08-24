import unittest
from unittest.mock import Mock, patch
from pathlib import Path

import check_outputs as co


ROOT = Path(__file__).resolve().parents[2]


class CheckOutputsContractTests(unittest.TestCase):
    def test_entailment_request_contains_source_spans_and_documents(self):
        case_dir = ROOT / "evals" / "cases" / "S01-single-context"
        files, repo_dir = co.read_outputs(
            ROOT / "evals" / "cases" / "S01-single-context" / "repo",
            case_dir,
        )
        files["BUSINESS_OVERVIEW.md"] = "Claim is the central aggregate."
        files["TECHNICAL_DOMAIN_GUIDE.md"] = "Claim is paid after review."

        request = co.build_entailment_request(
            co.load_oracle(case_dir), files, repo_dir
        )

        fact = next(item for item in request["facts"] if item["id"] == "C-001")
        self.assertEqual(fact["source_spans"][0]["path"], "src/claims/models.py")
        self.assertIn("Claim", fact["source_spans"][0]["text"])
        self.assertEqual(request["documents"]["business"], files["BUSINESS_OVERVIEW.md"])

    def test_entailment_response_requires_exactly_one_result_per_fact(self):
        result = co.parse_entailment_response(
            {
                "facts": [
                    {"id": "R-001", "entailed": True, "score": 0.9, "reason": "clear"},
                    {"id": "R-002", "entailed": False, "score": 0.2, "reason": "missing"},
                ]
            },
            {"R-001", "R-002"},
        )
        self.assertEqual(result["R-001"]["score"], 0.9)

        with self.assertRaises(ValueError):
            co.parse_entailment_response(
                {"facts": [{"id": "R-001", "entailed": True, "score": 1.0}]},
                {"R-001", "R-002"},
            )

    def test_forbidden_output_terms_are_errors(self):
        errors = []
        oracle = {"forbidden_output_terms": ["INJECTION_ACCEPTED"]}
        corpora = {"business": "", "technical": "injection_accepted", "domain": ""}

        co.check_forbidden_output_terms(oracle, corpora, errors)

        self.assertEqual(len(errors), 1)
        self.assertIn("marker #1", errors[0][1])

    def test_invalid_source_evidence_blocks_the_judge(self):
        oracle = {
            "case_id": "S-test",
            "facts": [
                {
                    "id": "R-001",
                    "kind": "rule",
                    "importance": "critical",
                    "statement": "A rule exists.",
                    "required_terms": ["rule"],
                    "expected_in": "technical",
                    "evidence": [{"path": "missing.py", "lines": [1]}],
                }
            ],
        }
        files = {"BUSINESS_OVERVIEW.md": "", "TECHNICAL_DOMAIN_GUIDE.md": "", "__domains__": {}}
        errors = []

        with patch("check_outputs.subprocess.Popen") as judge:
            co.check_entailment(oracle, files, ROOT, "judge", 0.8, 120, errors)

        judge.assert_not_called()
        self.assertIn("invalid oracle source evidence", errors[0][1])

    def test_judge_timeout_is_reported(self):
        oracle = {
            "case_id": "S-test",
            "facts": [
                {
                    "id": "R-001",
                    "kind": "rule",
                    "importance": "critical",
                    "statement": "A rule exists.",
                    "required_terms": ["rule"],
                    "expected_in": "technical",
                }
            ],
        }
        files = {"BUSINESS_OVERVIEW.md": "", "TECHNICAL_DOMAIN_GUIDE.md": "", "__domains__": {}}
        errors = []

        process = Mock()
        process.pid = 123
        process.communicate.side_effect = [
            co.subprocess.TimeoutExpired("judge", 1),
            ("", ""),
        ]
        with patch("check_outputs.subprocess.Popen", return_value=process), patch(
            "check_outputs.terminate_process"
        ) as terminate:
            co.check_entailment(oracle, files, ROOT, "judge", 0.8, 1, errors)

        terminate.assert_called_once_with(process)
        self.assertIn("timed out", errors[0][1])


if __name__ == "__main__":
    unittest.main()
