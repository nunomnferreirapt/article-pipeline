"""Tests for the fact-check gate."""

from __future__ import annotations

from pathlib import Path

from article_pipeline.check import check_run, needs_citation, split_sentences
from article_pipeline.cli import main
from conftest import CLAIMS_MD, DRAFT_MD, SOURCES_MD, write_run

REPO = Path(__file__).resolve().parents[1]


def kinds(run_dir: Path) -> list[str]:
    return [problem.kind for problem in check_run(run_dir).problems]


def test_passing_run_writes_pass_and_exits_zero(passing_run: Path, capsys) -> None:
    assert main(["check", str(passing_run)]) == 0
    factcheck = (passing_run / "factcheck.md").read_text(encoding="utf-8")
    assert "Result: PASS" in factcheck
    assert "None." in factcheck
    assert capsys.readouterr().out.startswith("PASS")


def test_sample_run_passes() -> None:
    report = check_run(REPO / "examples" / "sample-run")
    assert report.passed, [str(p) for p in report.problems]
    assert report.claims >= 6
    assert report.verified_quotes == report.claims


def test_unknown_source_id_in_draft_fails(tmp_path: Path) -> None:
    draft = DRAFT_MD + "\nA closing thought with a stray citation. [S9]\n"
    run_dir = write_run(tmp_path / "run", draft=draft)
    assert "unknown source" in kinds(run_dir)
    assert main(["check", str(run_dir)]) == 1
    assert "Result: FAIL" in (run_dir / "factcheck.md").read_text(encoding="utf-8")


def test_uncited_number_and_year_fail(tmp_path: Path) -> None:
    draft = DRAFT_MD + "\nAbout 40 percent never looked back. The survey ran in 2025.\n"
    problems = check_run(write_run(tmp_path / "run", draft=draft)).problems
    uncited = [p.detail for p in problems if p.kind == "uncited sentence"]
    assert len(uncited) == 2
    assert all(detail.startswith("contains a number") for detail in uncited)


def test_uncited_title_case_word_fails(tmp_path: Path) -> None:
    draft = DRAFT_MD + "\nThe crews in Northfield adopted it first.\n"
    problems = check_run(write_run(tmp_path / "run", draft=draft)).problems
    assert any("'Northfield'" in p.detail for p in problems)


def test_sentence_initial_capital_does_not_need_citation() -> None:
    assert needs_citation("Connectivity in the field is unreliable.") is None
    assert needs_citation("The crews in Northfield adopted it first.") is not None
    assert needs_citation("It took 3 days.") == "contains a number"


def test_headings_are_not_checked(tmp_path: Path) -> None:
    draft = "## Lessons From 140 Crews\n\n" + DRAFT_MD
    assert check_run(write_run(tmp_path / "run", draft=draft)).passed


def test_citation_before_or_after_the_period_both_count() -> None:
    sentences = split_sentences("First 1 [S1]. Second 2. [S2] Third 3.5 units [S1].")
    assert sentences == ["First 1 [S1].", "Second 2. [S2]", "Third 3.5 units [S1]."]
    assert all(needs_citation(s) is not None for s in sentences)


def test_quote_not_found_fails(tmp_path: Path) -> None:
    claims = CLAIMS_MD.replace(
        "87 reported at least one offline hour a day",
        "87 reported at least two offline hours a day",
    )
    problems = check_run(write_run(tmp_path / "run", claims=claims)).problems
    assert [p.kind for p in problems] == ["quote not found"]
    assert "C1" in problems[0].location


def test_quote_matches_across_whitespace_and_case(tmp_path: Path) -> None:
    claims = CLAIMS_MD.replace(
        '"Of the 140 crews surveyed, 87 reported at least one offline hour a day."',
        '"OF THE 140 CREWS   SURVEYED,\t 87 reported at least one offline hour a day."',
    )
    report = check_run(write_run(tmp_path / "run", claims=claims))
    assert report.passed, [str(p) for p in report.problems]
    assert report.verified_quotes == 2
    assert report.skipped_remote_quotes == 1


def test_claim_with_unknown_source_fails(tmp_path: Path) -> None:
    claims = CLAIMS_MD.replace("- Source: [S2]", "- Source: [S7]")
    problems = check_run(write_run(tmp_path / "run", claims=claims)).problems
    assert [p.kind for p in problems] == ["unknown source"]
    assert "claims.md" in problems[0].location


def test_missing_claims_and_draft_fail(tmp_path: Path) -> None:
    run_dir = write_run(tmp_path / "run")
    (run_dir / "claims.md").unlink()
    (run_dir / "draft.md").unlink()
    assert kinds(run_dir) == ["missing file", "missing file"]
