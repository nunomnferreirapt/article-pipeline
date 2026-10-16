"""The fact-check gate.

Three deterministic checks on a run folder:

1. Every `[S#]` citation in draft.md names a source listed in sources.md.
2. Every sentence in draft.md that carries a number, a percentage, a year, or a
   capitalized word that is not the first word of the sentence has at least
   one citation. Headings are skipped.
3. Every quote in claims.md is present, after whitespace and case
   normalization, in its source file when that source is local. Remote
   sources are not fetched; the gate never touches the network.

The result is written to factcheck.md as PASS or FAIL with the list of
problems. Nothing here calls a model.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from .run import CITATION, SOURCE_ID, normalize, read_claims, read_sources

SENTENCE_END = re.compile(r"[.!?]+(?:\s*\[S\d+\])*(?=\s|$)")
DIGIT = re.compile(r"\d")
TITLE_CASE_WORD = re.compile(r"\b[A-Z][a-z]+\b")
LIST_MARKER = re.compile(r"^(\s*(?:[-*+]|\d+[.)])\s+|\s*>\s*)")


@dataclass
class Problem:
    """One thing the gate found wrong."""

    kind: str
    location: str
    detail: str

    def __str__(self) -> str:
        return f"{self.kind} ({self.location}): {self.detail}"


@dataclass
class Report:
    """Outcome of one gate run."""

    problems: list[Problem] = field(default_factory=list)
    sentences: int = 0
    cited_sentences: int = 0
    claims: int = 0
    verified_quotes: int = 0
    skipped_remote_quotes: int = 0

    @property
    def passed(self) -> bool:
        return not self.problems

    @property
    def verdict(self) -> str:
        return "PASS" if self.passed else "FAIL"

    def to_markdown(self, checked_on: date | None = None) -> str:
        checked_on = checked_on or date.today()
        lines = [
            "# Fact check",
            "",
            f"Result: {self.verdict}",
            "",
            f"Checked on {checked_on.isoformat()} by `article-pipeline check`.",
            "",
            f"- draft.md: {self.sentences} sentences, {self.cited_sentences} cited",
            f"- claims.md: {self.claims} claims, {self.verified_quotes} quotes "
            f"verified against local sources, {self.skipped_remote_quotes} "
            "remote (not fetched)",
            "",
            "## Problems",
            "",
        ]
        if self.problems:
            lines.extend(f"- {problem}" for problem in self.problems)
        else:
            lines.append("None.")
        lines.append("")
        return "\n".join(lines)


def split_sentences(text: str) -> list[str]:
    """Split prose into sentences, keeping trailing `[S#]` citations attached.

    A terminator only counts when followed by whitespace or the end of the
    text, so decimals such as 3.5 do not split.
    """
    sentences: list[str] = []
    start = 0
    for match in SENTENCE_END.finditer(text):
        sentences.append(text[start : match.end()].strip())
        start = match.end()
    tail = text[start:].strip()
    if tail:
        sentences.append(tail)
    return [s for s in sentences if s]


def draft_paragraphs(text: str) -> list[str]:
    """Return the prose paragraphs of a Markdown draft, headings removed."""
    paragraphs: list[str] = []
    current: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            if current:
                paragraphs.append(" ".join(current))
                current = []
            continue
        current.append(LIST_MARKER.sub("", line))
    if current:
        paragraphs.append(" ".join(current))
    return paragraphs


def needs_citation(sentence: str) -> str | None:
    """Return why a sentence needs a citation, or None if it does not."""
    bare = CITATION.sub("", sentence)
    if DIGIT.search(bare):
        return "contains a number"
    first_word = re.search(r"[A-Za-z][A-Za-z'-]*", bare)
    if first_word is None:
        return None
    rest = bare[first_word.end() :]
    capitalized = TITLE_CASE_WORD.findall(rest)
    if capitalized:
        return f"contains the capitalized word '{capitalized[0]}'"
    return None


def check_draft(run_dir: Path, report: Report) -> None:
    draft_path = run_dir / "draft.md"
    if not draft_path.is_file():
        report.problems.append(Problem("missing file", "draft.md", "not found"))
        return
    sources = read_sources(run_dir)
    text = draft_path.read_text(encoding="utf-8")

    for cited in sorted(set(SOURCE_ID.findall(text))):
        if cited not in sources:
            report.problems.append(
                Problem("unknown source", "draft.md", f"[{cited}] is not in sources.md")
            )

    for paragraph in draft_paragraphs(text):
        for sentence in split_sentences(paragraph):
            report.sentences += 1
            if CITATION.search(sentence):
                report.cited_sentences += 1
                continue
            reason = needs_citation(sentence)
            if reason:
                report.problems.append(
                    Problem("uncited sentence", "draft.md", f"{reason}: {sentence}")
                )


def check_claims(run_dir: Path, report: Report) -> None:
    claims_path = run_dir / "claims.md"
    if not claims_path.is_file():
        report.problems.append(Problem("missing file", "claims.md", "not found"))
        return
    sources = read_sources(run_dir)
    claims = read_claims(run_dir)
    report.claims = len(claims)

    for claim in claims:
        where = f"claims.md:{claim.line} {claim.id}"
        if claim.source_id is None:
            report.problems.append(Problem("missing source", where, "no [S#] given"))
            continue
        source = sources.get(claim.source_id)
        if source is None:
            report.problems.append(
                Problem("unknown source", where, f"[{claim.source_id}] is not in sources.md")
            )
            continue
        if not claim.quote:
            report.problems.append(Problem("missing quote", where, "quote is empty"))
            continue
        if source.is_remote:
            report.skipped_remote_quotes += 1
            continue
        source_path = source.local_path(run_dir)
        assert source_path is not None
        if not source_path.is_file():
            report.problems.append(
                Problem("missing source file", where, f"{source.location} not found")
            )
            continue
        haystack = normalize(source_path.read_text(encoding="utf-8"))
        if normalize(claim.quote) in haystack:
            report.verified_quotes += 1
        else:
            report.problems.append(
                Problem(
                    "quote not found",
                    where,
                    f"not in {source.location}: \"{claim.quote}\"",
                )
            )


def check_run(run_dir: Path) -> Report:
    """Run every check and return the report without writing anything."""
    report = Report()
    if not (run_dir / "sources.md").is_file():
        report.problems.append(Problem("missing file", "sources.md", "not found"))
    check_draft(run_dir, report)
    check_claims(run_dir, report)
    return report


def check_and_write(run_dir: Path) -> Report:
    """Run the gate and write factcheck.md into the run folder."""
    report = check_run(run_dir)
    (run_dir / "factcheck.md").write_text(report.to_markdown(), encoding="utf-8")
    return report
