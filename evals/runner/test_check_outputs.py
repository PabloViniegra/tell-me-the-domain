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


S01_REPO = ROOT / "evals" / "cases" / "S01-single-context" / "repo"


def messages(errors):
    return [message for _, message in errors]


class ReferenceFormatTests(unittest.TestCase):
    def check(self, reference):
        errors = []
        co.check_references_against_repo("TECHNICAL_DOMAIN_GUIDE.md", reference, S01_REPO, errors)
        return messages(errors)

    def test_column_suffix_is_not_read_as_a_range(self):
        self.assertEqual(self.check("`src/claims/service.py:24:5`"), [])

    def test_line_spans_are_validated(self):
        self.assertEqual(self.check("`src/claims/service.py:24-29`"), [])
        self.assertIn("end line is out of range", self.check("`src/claims/service.py:24-900`")[0])
        self.assertIn("end line is out of range", self.check("`src/claims/service.py:24-10`")[0])


class SurpriseParityTests(unittest.TestCase):
    def files(self, business, technical):
        heading = f"## {co.SURPRISE_HEADING}\n"
        return {
            "BUSINESS_OVERVIEW.md": heading + business,
            "TECHNICAL_DOMAIN_GUIDE.md": heading + technical,
            "__domains__": {},
        }

    def test_nested_bullets_do_not_count_against_the_cap(self):
        business = "1. *A.* text\n   - detail one\n   - detail two\n   - detail three\n"
        errors = []
        co.check_surprise_cap_and_parity(self.files(business, "1. *A.* code view\n"), errors)
        self.assertEqual(errors, [])

    def test_a_following_section_ends_the_surprise_list(self):
        business = "1. *A.* x\n\n## Glossary\n- one\n- two\n- three\n"
        errors = []
        co.check_surprise_cap_and_parity(self.files(business, "1. *A.* y\n"), errors)
        self.assertEqual(errors, [])

    def test_order_must_match(self):
        errors = []
        co.check_surprise_cap_and_parity(
            self.files("1. *A.* x\n2. *B.* y\n", "1. *B.* y\n2. *A.* x\n"), errors
        )
        self.assertIn("same order", messages(errors)[0])


class IdDefinitionTests(unittest.TestCase):
    def check(self, technical, business):
        errors = []
        co.check_id_cross_reference(
            {"TECHNICAL_DOMAIN_GUIDE.md": technical, "BUSINESS_OVERVIEW.md": business, "__domains__": {}},
            errors,
        )
        return messages(errors)

    def test_ids_are_required_even_when_the_guide_defines_none(self):
        found = self.check("No IDs here.", "See R-999.")
        self.assertTrue(any("BUSINESS_OVERVIEW.md" in m and "R-999" in m for m in found))

    def test_header_legend_neither_defines_nor_references_ids(self):
        legend = "> IDs look like `R-001`, `C-001` or `L-001`.\n\n## Rules\n"
        found = self.check(legend + "| R-001 | rule |", legend + "R-001 and L-001.")
        self.assertTrue(any("L-001" in m and "C-001" not in m and "R-001" not in m for m in found))

    def test_absence_report_with_only_missing_facts_passes(self):
        legend = "> Every rule carries an ID (`R-001`, `C-001`).\n\n## Open questions\n"
        self.assertEqual(self.check(legend + "1. **F-001 — nothing here**", legend + "F-001"), [])

    def test_ids_in_inline_code_count_outside_the_header(self):
        technical = "## Lifecycles\n### Life of a handler outcome (`L-002`)\n"
        self.assertEqual(self.check(technical, "See `L-002`."), [])

    def test_ids_in_tables_headings_and_prose_define_ids(self):
        technical = (
            "| R-002 | Tenant reader (A-001) |\n### Life of a ticket (L-001)\n"
            "**No lifecycle exists (L-002).**\n"
        )
        self.assertEqual(self.check(technical, "R-002, A-001, L-001 and L-002."), [])


class MetadataTests(unittest.TestCase):
    def test_per_context_files_need_date_and_mode(self):
        errors = []
        co.check_meta("[domain]billing.md", "# Billing\nNo header.", errors)
        self.assertEqual(len(errors), 2)

    def test_written_out_dates_count_as_dates(self):
        for header in ("dated **10 November 2026**", "as of Nov 10, 2026"):
            errors = []
            co.check_meta("X.md", f"> Tree {header}. Analysis mode: complete context.", errors)
            self.assertEqual(errors, [], header)

    def test_plain_words_are_not_commit_hashes(self):
        errors = []
        co.check_meta("X.md", "> Built from the defaced branch. Analysis mode: complete context.", errors)
        self.assertIn("missing commit hash or date", messages(errors)[0])


class DocumentChecksTests(unittest.TestCase):
    def run_checks(self, out_dir, domains):
        errors = []
        files = {"__domains__": domains}
        co.check_documents(files, out_dir, S01_REPO, {"[Concept]"}, errors)
        return messages(errors)

    def test_per_context_links_resolve_from_the_domains_folder(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / "domains").mkdir()
            (out / "BUSINESS_OVERVIEW.md").write_text("x")
            header = "> 2026-11-10. Analysis mode: complete context.\n"
            found = self.run_checks(out, {"billing.md": header + "[up](../BUSINESS_OVERVIEW.md)"})
            self.assertEqual(found, [])
            found = self.run_checks(out, {"billing.md": header + "[bad](BUSINESS_OVERVIEW.md)"})
            self.assertTrue(any("broken relative link" in m for m in found))

    def test_per_context_files_are_checked_for_metadata(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            found = self.run_checks(Path(tmp), {"billing.md": "# Billing\n"})
            self.assertTrue(any("[domain]billing.md: missing commit hash or date" in m for m in found))


class PlaceholderTests(unittest.TestCase):
    def test_placeholders_come_from_the_skill_templates(self):
        placeholders = co.load_placeholders()
        self.assertIn("[Product name]", placeholders)
        self.assertIn("[...]", placeholders)
        self.assertNotIn("[*]", placeholders)

    def test_unfilled_templates_fail_and_filled_text_passes(self):
        placeholders = co.load_placeholders()
        template_dir = ROOT / co.TEMPLATE_SUBDIR
        for template in template_dir.glob("*.template.md"):
            errors = []
            co.check_no_placeholders(template.name, template.read_text(encoding="utf-8"), placeholders, errors)
            self.assertTrue(errors, template.name)
        errors = []
        filled = (
            "| C-001 | Claim | A[Trigger] --> B[Step] | [the docs](TECHNICAL_DOMAIN_GUIDE.md) | [*] --> Draft |\n"
            "See [`../BUSINESS_OVERVIEW.md`](../BUSINESS_OVERVIEW.md). Body: "
            '`{"status": "rejected", "missing": [...]}` and `items[n]`.'
        )
        co.check_no_placeholders("BUSINESS_OVERVIEW.md", filled, placeholders, errors)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
