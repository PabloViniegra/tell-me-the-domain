#!/usr/bin/env python3
import argparse
import json
import re
import sys
from pathlib import Path


PLACEHOLDERS = [
    "[Product name]",
    "[Context name]",
    "[Concept]",
    "[Rule]",
    "[Name]",
    "[Term]",
    "[Role]",
    "[commit / date]",
    "[commit/date]",
    "[commit]",
    "[Name]",
    "[commit / date]",
    "[Source]",
    "[Destination context]",
    "[Other contexts, or \"none\"]",
    "[n]",
    "[n]",
    "[n]",
    "[status]",
    "[what remains, if anything]",
    "[Bounded contexts and products analyzed.]",
    "[Modules and deployables owned by this context.]",
    "[Areas of this context intentionally not read and why.]",
    "[Areas intentionally not read and why — atlas mode only.]",
    "[Areas intentionally not read and why.]",
    "[Missing tools, unavailable contracts, or facts that could not be established from the repository.]",
    "[Missing tools, unavailable contracts, or facts that could not be established from this context.]",
    "[Contexts and deployables analyzed.]",
    "[Code map for the developer-side output.]",
    "[Highlighted journeys in the next section]",
    "[High-level]",
    "[Narrate the same flow in two or three sentences: what starts it, what has to be true along the way, what the business gets at the end. Include the failure and exception paths that change the outcome.]",
    "[Tradeoff: this section includes the failure and exception paths that change the outcome.]",
    "[NIT]",
    "[path/to/file.ext:line]",
    "[mode]",
    "[complete context / repository atlas]",
    "[complete context/repository atlas]",
    "[scope]",
    "[date]",
    "[trigger]",
    "[outcome]",
    "[actor]",
    "[Who starts it]",
    "[What starts it]",
    "[What the business gets]",
    "[What happens when violated]",
    "[Source of the rule]",
    "[Where defined (see technical guide)]",
    "[Claimed mechanism]",
    "[Reviewed]",
    "[Modified]",
    "[Source: buyer, reviewer, scheduler, etc.]",
    "[NIT-001]",
    "[Critical]",
    "[incidental]",
    "[Mode reference]",
    "[sentence]",
    "[One-line]",
    "[Concept meaning]",
    "[paths to source code files]",
    "[Method]",
    "[Action]",
    "[Method of enforcement]",
    "[Concrete example]",
    "[Status]",
    "[complete, partial, blocked, out-of-scope, no longer applicable]",
    "[some code path]",
    "[adapt to the case]",
    "[example counterparty file:line]",
    "[path/to/source.py]",
    "[Template approach]",
    "[organization-team]",
    "[ingestion-team]",
    "[Version]",
    "[Rule]",
    "[Concept]",
    "[Exclusions]",
    "[Claim type to focus on]",
    "[Channel]",
    "[SLA parameters]",
    "[inbound / outbound]",
    "[Business role]",
    "[Adapter]",
    "[Adapter or gateway]",
    "[Per-minute rate cap]",
    "[HTTP code]",
    "[Trigger type]",
    "[Cron or event]",
    "[Business effect]",
    "[field name]",
    "[requirement string]",
    "[maximum spend]",
    "[outcome]",
    "[outcome that matters]",
    "[delivery confirmation source]",
    "[failure]",
    "[recovery]",
    "[actor, role, system]",
    "[diagnosis source]",
    "[expected outcome]",
    "[duration before pause kicks in]",
    "[how long it can persist]",
    "[rate limiter per minute]",
    "[subscription tier, by region]",
    "[Blocking reason]",
    "[or \"None\"]",
    "[other contexts, or \"none\"]",
    "[other contexts, or 'none']",
    "[Source context]",
    "[destination-context]",
    "[Reading route to destination]",
    "[set]",
    "[expiration pattern]",
    "[outcome / end state]",
    "[Next checkpoint]",
    "[reference to next context]",
    "[404, 409, etc.]",
    "[invariant label]",
    "[error or HTTP status]",
    "[expiration rule for test]",
    "[test directory path]",
    "[reference lines]",
    "[hash or version reference]",
    "[trace example]",
    "[DRI for response]",
    "[Inbound/outbound address]",
    "[note one example with file:line]",
    "[Failure scenario]",
    "[expected outcome when missing]",
    "[recovery when delayed]",
    "[Subject area]",
    "[Source reads]",
    "[target writes]",
    "[field name with type]",
    "[maximum attempt]",
    "[condition for allow / refuse]",
    "[Captured event type]",
    "[SLA duration]",
    "[failure impact per contract]",
    "[fixing commit]",
    "[fixing patch release]",
    "[team, individual, automation]",
    "[retry depth, idempotency token]",
    "[name and path of the file with the rule]",
    "[test that asserts the violation]",
    "[explanation of the unit conversion]",
    "[adapter framework]",
    "[step onboarding of new joiners]",
    "[reference ADR or policy doc]",
]

SURPRISE_HEADING = "Three things that would surprise a newcomer"
PATH_LINE_RE = re.compile(r"`([\w./\-]+\.[a-zA-Z0-9]{1,10}):(\d+)(?::(\d+))?`")
RELATIVE_LINK_RE = re.compile(r"\[(?P<text>[^\]]+)\]\((?P<href>[^)]+)\)")
BUSINESS_PATH_RE = re.compile(r"`[\w./\-]+\.[a-zA-Z0-9]{1,10}:\d+(?::\d+)?`")
BUSINESS_PATH_BARE_RE = re.compile(r"(?<!`)[\w./\-]+\.[a-zA-Z0-9]{1,10}:\d+(?::\d+)?")
COMMIT_RE = re.compile(r"\b[0-9a-f]{7,40}\b")
DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
MODE_BLOCKQUOTE_RE = re.compile(r"^>\s*.*?(complete context|repository atlas)", re.MULTILINE | re.IGNORECASE)
LINK_SKIP_PREFIXES = ("http://", "https://", "mailto:", "#")
COVERAGE_KEYWORDS = ["complete", "partial", "blocked", "not-found-after-search", "not-applicable", "out-of-scope"]
ID_RE = re.compile(r"\b([RCPTALF])-(\d{1,4})\b")

EXPECTED_DEFAULTS = [
    "BUSINESS_OVERVIEW.md",
    "TECHNICAL_DOMAIN_GUIDE.md",
]


def load_oracle(case_dir: Path) -> dict:
    with (case_dir / "oracle.json").open() as f:
        return json.load(f)


def load_questions(case_dir: Path) -> list:
    p = case_dir / "questions.json"
    return json.loads(p.read_text()) if p.exists() else []


def read_outputs(out_dir: Path, case_dir: Path):
    repo_dir = case_dir / "repo"
    files = {}
    for name in EXPECTED_DEFAULTS:
        p = out_dir / name
        files[name] = p.read_text() if p.exists() else None
    domains_dir = out_dir / "domains"
    domain_files = {}
    if domains_dir.exists():
        for p in sorted(domains_dir.glob("*.md")):
            domain_files[p.name] = p.read_text()
    files["__domains__"] = domain_files
    return files, repo_dir


def check_kind(name: str, kind: str, errors: list) -> None:
    errors.append((kind, f"{name}: placeholder {('placeholder' if False else 'check')} failed"))


def add(errors: list, kind: str, message: str) -> None:
    errors.append((kind, message))


def check_no_placeholders(name: str, text: str, errors: list) -> None:
    if text is None:
        add(errors, "structural", f"{name}: missing")
        return
    for placeholder in PLACEHOLDERS:
        if placeholder in text:
            add(errors, "structural", f"{name}: contains placeholder {placeholder!r}")


def check_paths(name: str, text: str, errors: list) -> None:
    if text is None:
        return
    business_register = name == "BUSINESS_OVERVIEW.md" or name.startswith("[domain]")
    if business_register:
        if BUSINESS_PATH_RE.search(text):
            add(errors, "structural", f"{name}: business document contains a path:line reference; use IDs")
        if BUSINESS_PATH_BARE_RE.search(text):
            add(errors, "structural", f"{name}: business document mentions a path:line without backticks")


def check_references_against_repo(name: str, text: str, repo_dir: Path, errors: list) -> None:
    if text is None or name != "TECHNICAL_DOMAIN_GUIDE.md":
        return
    matches = PATH_LINE_RE.findall(text)
    for path, start, end in matches:
        if path.startswith("http"):
            continue
        target = repo_dir / path
        if not target.exists():
            add(errors, "structural", f"{name}: reference `{path}:{start}` but {path} is not in the repo")
            continue
        lines = target.read_text().splitlines()
        line_no = int(start)
        if line_no < 1 or line_no > len(lines):
            add(errors, "structural", f"{name}: reference `{path}:{start}` is out of range (file has {len(lines)} lines)")
            continue
        if end:
            end_no = int(end)
            if end_no < line_no or end_no > len(lines):
                add(errors, "structural", f"{name}: reference `{path}:{start}:{end}` end line is out of range")


def check_relative_links(name: str, text: str, out_dir: Path, errors: list) -> None:
    if text is None:
        return
    for m in RELATIVE_LINK_RE.finditer(text):
        href = m.group("href").strip()
        if not href or href.startswith(LINK_SKIP_PREFIXES):
            continue
        clean = href.split("#", 1)[0]
        if not clean:
            continue
        target = (out_dir / clean).resolve()
        if not target.exists():
            add(errors, "structural", f"{name}: broken relative link -> {href}")


def check_meta(name: str, text: str, errors: list) -> None:
    if text is None:
        return
    if name.startswith("[domain]"):
        return
    if not (COMMIT_RE.search(text) or DATE_RE.search(text)):
        add(errors, "structural", f"{name}: missing commit hash or date")
    if not MODE_BLOCKQUOTE_RE.search(text):
        add(errors, "structural", f"{name}: missing analysis mode in the header blockquote (complete context / repository atlas)")


def check_coverage_matrix(name: str, text: str, errors: list) -> None:
    if text is None or name != "TECHNICAL_DOMAIN_GUIDE.md":
        return
    head_match = re.search(r"^##\s+Coverage matrix\s*$", text, re.MULTILINE)
    if not head_match:
        add(errors, "structural", f"{name}: missing 'Coverage matrix' section")
        return
    section_start = head_match.end()
    next_head = re.search(r"^##\s+", text[section_start:], re.MULTILINE)
    section_end = section_start + (next_head.start() if next_head else len(text) - section_start)
    section_text = text[section_start:section_end].lower()
    if not any(k in section_text for k in COVERAGE_KEYWORDS):
        add(errors, "structural", f"{name}: coverage matrix section has no recognized statuses")


def extract_surprise_items(text: str) -> list:
    if not text:
        return []
    heading_re = re.compile(r"^##\s+" + re.escape(SURPRISE_HEADING) + r"\s*$", re.MULTILINE)
    match = heading_re.search(text)
    if not match:
        return []
    start = match.end()
    next_head = re.search(r"^##\s+", text[start:], re.MULTILINE)
    end = start + (next_head.start() if next_head else len(text))
    section = text[start:end]
    items = []
    for raw in section.split("\n"):
        s = raw.strip()
        if not s:
            continue
        if re.match(r"^\d+\.\s", s) or s.startswith("- "):
            items.append(re.sub(r"^(\d+\.\s|-\s)", "", s).strip())
    return [item for item in items if item]


def extract_headline(item: str) -> str:
    m = re.search(r"\*(.+?)\*", item)
    if m:
        return m.group(1).strip()
    return item.split("\n")[0].strip()


def normalize_for_compare(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def check_surprise_cap_and_parity(files: dict, errors: list) -> None:
    business = extract_surprise_items(files.get("BUSINESS_OVERVIEW.md"))
    technical = extract_surprise_items(files.get("TECHNICAL_DOMAIN_GUIDE.md"))
    if len(business) > 3:
        add(errors, "structural", f"BUSINESS_OVERVIEW.md: lists {len(business)} 'Three things' items; hard cap is 3")
    if len(technical) > 3:
        add(errors, "structural", f"TECHNICAL_DOMAIN_GUIDE.md: lists {len(technical)} 'Three things' items; hard cap is 3")
    if not business or not technical:
        return
    business_headlines = {normalize_for_compare(extract_headline(b)) for b in business}
    technical_headlines = {normalize_for_compare(extract_headline(t)) for t in technical}
    missing_in_tech = business_headlines - technical_headlines
    if missing_in_tech:
        add(errors, "structural", f"TECHNICAL_DOMAIN_GUIDE.md: surprise items not aligned with BUSINESS_OVERVIEW.md (missing: {sorted(missing_in_tech)})")
    missing_in_biz = technical_headlines - business_headlines
    if missing_in_biz:
        add(errors, "structural", f"BUSINESS_OVERVIEW.md: surprise items not aligned with TECHNICAL_DOMAIN_GUIDE.md (missing: {sorted(missing_in_biz)})")


def check_overview_context_bidi(files: dict, out_dir: Path, errors: list) -> None:
    domains = files["__domains__"]
    if not domains:
        return
    overview_targets = []
    for name in ("BUSINESS_OVERVIEW.md", "TECHNICAL_DOMAIN_GUIDE.md"):
        text = files.get(name)
        if text is None:
            continue
        linked = [href for href in re.findall(r"\]\(([^)]+)\)", text) if "domains/" in href]
        overview_targets.append((name, sorted(set(linked))))
    expected = sorted(f"domains/{d}.md" for d in domains.keys() if not d.endswith(".md"))
    expected = sorted([f"domains/{d}" for d in domains])
    for name, linked in overview_targets:
        for d in expected:
            if not any(d in l for l in linked):
                add(errors, "structural", f"{name}: does not link to {d} (per-context bidirectional linking required)")
    for d_name, d_text in domains.items():
        expected_overviews = ["../BUSINESS_OVERVIEW.md", "../TECHNICAL_DOMAIN_GUIDE.md"]
        for ov in expected_overviews:
            if ov not in d_text:
                add(errors, "structural", f"domains/{d_name}: missing back-reference to {ov}")


def extract_ids(text: str) -> set:
    if not text:
        return set()
    return {f"{kind}-{num}" for kind, num in ID_RE.findall(text)}


def check_id_cross_reference(files: dict, errors: list) -> None:
    technical_text = files.get("TECHNICAL_DOMAIN_GUIDE.md") or ""
    defined = extract_ids(technical_text)
    if not defined:
        return
    consumers = {"BUSINESS_OVERVIEW.md": files.get("BUSINESS_OVERVIEW.md") or ""}
    for d_name, d_text in files["__domains__"].items():
        consumers[f"domains/{d_name}"] = d_text
    for consumer_name, consumer_text in consumers.items():
        if not consumer_text:
            continue
        referenced = extract_ids(consumer_text)
        undefined = referenced - defined
        if undefined:
            sample = sorted(undefined)[:5]
            add(errors, "structural", f"{consumer_name}: IDs not defined in TECHNICAL_DOMAIN_GUIDE.md (sample: {sample})")


def collect_search_corpus(files: dict) -> dict:
    business = (files.get("BUSINESS_OVERVIEW.md") or "").lower()
    technical = (files.get("TECHNICAL_DOMAIN_GUIDE.md") or "").lower()
    domain_corpus = " ".join(files["__domains__"].values()).lower()
    return {
        "business": business,
        "technical": technical,
        "domain": domain_corpus,
    }


def corpus_for(scope: str, corpora: dict) -> str:
    if scope == "business":
        return corpora["business"] + " " + corpora["domain"]
    if scope == "technical":
        return corpora["technical"] + " " + corpora["domain"]
    return corpora["business"] + " " + corpora["technical"] + " " + corpora["domain"]


def check_oracle(oracle: dict, corpora: dict, errors: list) -> tuple:
    per_kind = {}
    per_fact_status = []
    critical_missed = []
    for fact in oracle.get("facts", []):
        scope = fact["expected_in"]
        terms = [t.lower() for t in fact["required_terms"]]
        if scope == "both":
            business_present = [t for t in terms if t in corpora["business"] or t in corpora["domain"]]
            technical_present = [t for t in terms if t in corpora["technical"] or t in corpora["domain"]]
            missing = [fact["required_terms"][i] for i, t in enumerate(terms)
                        if t not in business_present and t not in technical_present]
            present = set(business_present) | set(technical_present)
        else:
            text = corpus_for(scope, corpora)
            missing = [fact["required_terms"][i] for i, t in enumerate(terms) if t not in text]
            present = set(terms) - set(missing)
        kind = fact["kind"]
        per_kind.setdefault(kind, [0, 0])
        per_kind[kind][1] += 1
        if not missing:
            per_kind[kind][0] += 1
            per_fact_status.append((fact["id"], "ok"))
        else:
            per_fact_status.append((fact["id"], "MISSING " + ", ".join(missing)))
            if fact["importance"] == "critical":
                critical_missed.append((fact["id"], missing))
    if critical_missed:
        ids = [i for i, _ in critical_missed]
        add(errors, "oracle", f"critical facts not recalled: {ids}")
    return per_kind, per_fact_status, critical_missed


def check_questions(questions: list, corpora: dict, errors: list) -> None:
    corpus = corpora["business"] + " " + corpora["technical"] + " " + corpora["domain"]
    for q in questions:
        missing = [t for t in q["must_contain"] if t.lower() not in corpus]
        if missing:
            add(errors, "oracle", f"question '{q['question'][:60]}' cannot be answered (missing: {missing})")


def run_case(case_dir: Path, out_dir: Path) -> int:
    errors: list = []
    oracle = load_oracle(case_dir)
    questions = load_questions(case_dir)
    files, repo_dir = read_outputs(out_dir, case_dir)

    for name, text in files.items():
        if name == "__domains__":
            for d_name, d_text in text.items():
                tagged_name = f"[domain]{d_name}"
                check_no_placeholders(tagged_name, d_text, errors)
                check_paths(tagged_name, d_text, errors)
                check_relative_links(tagged_name, d_text, out_dir, errors)
            continue
        check_no_placeholders(name, text, errors)
        check_paths(name, text, errors)
        check_references_against_repo(name, text, repo_dir, errors)
        check_relative_links(name, text, out_dir, errors)
        check_meta(name, text, errors)
        check_coverage_matrix(name, text, errors)

    check_surprise_cap_and_parity(files, errors)
    check_overview_context_bidi(files, out_dir, errors)
    check_id_cross_reference(files, errors)

    corpora = collect_search_corpus(files)
    per_kind, per_fact_status, critical_missed = check_oracle(oracle, corpora, errors)
    check_questions(questions, corpora, errors)

    structural = [m for kind, m in errors if kind == "structural"]
    oracle_errs = [m for kind, m in errors if kind == "oracle"]

    print(f"--- {case_dir.name} ---")
    print(f"structural errors: {len(structural)}")
    for m in structural:
        print(f"  - {m}")
    print(f"oracle errors: {len(oracle_errs)}")
    for m in oracle_errs:
        print(f"  - {m}")
    print("oracle recall by kind:")
    for kind, (hit, total) in sorted(per_kind.items()):
        pct = 100.0 * hit / total if total else 0.0
        print(f"  {kind:14s} {hit}/{total} ({pct:.0f}%)")
    for fid, status in per_fact_status:
        print(f"  {fid:8s} {status}")
    return 0 if not errors else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True, type=Path)
    parser.add_argument("--outputs", required=True, type=Path)
    args = parser.parse_args()
    return run_case(args.case.resolve(), args.outputs.resolve())


if __name__ == "__main__":
    sys.exit(main())
