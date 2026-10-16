"""Read the files of a run folder: sources.md and claims.md.

A run folder holds one article from brief to fact check. The file formats are
plain Markdown that a person can read and edit. This module parses the two
files the gate depends on.

sources.md has one table row per allowed source:

    | id | title | location |
    |----|-------|----------|
    | S1 | Survey notes | sources/s1-survey-notes.md |
    | S2 | Essay on limits | https://example.org/essay |

claims.md has one block per claim:

    ## C1
    - Claim: Most crews lose connectivity at least once a day.
    - Source: [S1]
    - Quote: "Of the 140 crews, 87 reported at least one offline hour a day."
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

SOURCE_ROW = re.compile(r"^\|\s*(S\d+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*$")
CLAIM_HEADING = re.compile(r"^##\s+(C\d+)\s*$")
CLAIM_FIELD = re.compile(r"^-\s*(Claim|Source|Quote)\s*:\s*(.*)$")
SOURCE_ID = re.compile(r"\[(S\d+)\]")
CITATION = re.compile(r"\[S\d+\]")


@dataclass(frozen=True)
class Source:
    """One allowed source. `location` is a URL or a path relative to the run."""

    id: str
    title: str
    location: str

    @property
    def is_remote(self) -> bool:
        return self.location.startswith(("http://", "https://"))

    def local_path(self, run_dir: Path) -> Path | None:
        if self.is_remote:
            return None
        return run_dir / self.location


@dataclass(frozen=True)
class Claim:
    """One claim with its verbatim quote and the source it comes from."""

    id: str
    claim: str
    source_id: str | None
    quote: str
    line: int


def parse_sources(text: str) -> dict[str, Source]:
    """Return sources by id from the text of sources.md."""
    sources: dict[str, Source] = {}
    for line in text.splitlines():
        match = SOURCE_ROW.match(line.strip())
        if match:
            source_id, title, location = match.groups()
            sources[source_id] = Source(source_id, title, location)
    return sources


def parse_claims(text: str) -> list[Claim]:
    """Return the claims listed in claims.md, in file order."""
    claims: list[Claim] = []
    current: dict[str, str] | None = None
    current_line = 0

    def flush() -> None:
        if current is None:
            return
        source_match = SOURCE_ID.search(current.get("Source", ""))
        claims.append(
            Claim(
                id=current["id"],
                claim=current.get("Claim", "").strip(),
                source_id=source_match.group(1) if source_match else None,
                quote=_strip_quotes(current.get("Quote", "")),
                line=current_line,
            )
        )

    for number, line in enumerate(text.splitlines(), start=1):
        heading = CLAIM_HEADING.match(line.strip())
        if heading:
            flush()
            current = {"id": heading.group(1)}
            current_line = number
            continue
        field = CLAIM_FIELD.match(line.strip())
        if field and current is not None:
            current[field.group(1)] = field.group(2)
    flush()
    return claims


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def normalize(text: str) -> str:
    """Lowercase and collapse whitespace, the only normalization the gate does."""
    return " ".join(text.lower().split())


def read_sources(run_dir: Path) -> dict[str, Source]:
    path = run_dir / "sources.md"
    if not path.is_file():
        return {}
    return parse_sources(path.read_text(encoding="utf-8"))


def read_claims(run_dir: Path) -> list[Claim]:
    path = run_dir / "claims.md"
    if not path.is_file():
        return []
    return parse_claims(path.read_text(encoding="utf-8"))
