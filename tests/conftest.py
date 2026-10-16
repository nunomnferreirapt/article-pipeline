"""Shared fixtures: a small synthetic run that passes the gate."""

from __future__ import annotations

from pathlib import Path

import pytest

SOURCE_TEXT = """# Survey notes: connectivity on small field crews (2025)

Of the 140 crews surveyed, 87 reported at least one offline hour a day.
Crews that moved to offline-first tools cut their end-of-day sync time
from 3.5 hours to 40 minutes on average.
"""

SOURCES_MD = """# Sources

| id | title | location |
|----|-------|----------|
| S1 | Survey notes | sources/s1-survey-notes.md |
| S2 | Essay on limits | https://example.org/essay |
"""

CLAIMS_MD = """# Claims

## C1
- Claim: Most surveyed crews lose connectivity at least once a day.
- Source: [S1]
- Quote: "Of the 140 crews surveyed, 87 reported at least one offline hour a day."

## C2
- Claim: Sync time fell sharply after the switch.
- Source: [S1]
- Quote: "cut their end-of-day sync time from 3.5 hours to 40 minutes on average"

## C3
- Claim: Offline-first has limits in regulated settings.
- Source: [S2]
- Quote: "offline-first is not a free lunch in regulated settings"
"""

DRAFT_MD = """# Why small field teams go offline-first

Connectivity in the field is unreliable. Of 140 crews surveyed, 87 lost
connectivity for at least an hour a day. [S1] The fix most crews chose was
to stop depending on the network at all.

End-of-day sync fell from 3.5 hours to 40 minutes on average [S1]. That is
not a small change for a crew that wants to go home.

There are limits. One essay argues that offline-first is not a free lunch
in regulated settings. [S2]
"""


def write_run(
    run_dir: Path,
    *,
    sources: str = SOURCES_MD,
    claims: str = CLAIMS_MD,
    draft: str = DRAFT_MD,
    source_text: str = SOURCE_TEXT,
) -> Path:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "sources").mkdir(exist_ok=True)
    (run_dir / "sources" / "s1-survey-notes.md").write_text(source_text, encoding="utf-8")
    (run_dir / "sources.md").write_text(sources, encoding="utf-8")
    (run_dir / "claims.md").write_text(claims, encoding="utf-8")
    (run_dir / "draft.md").write_text(draft, encoding="utf-8")
    return run_dir


@pytest.fixture
def passing_run(tmp_path: Path) -> Path:
    return write_run(tmp_path / "2026-10-16-offline-first")
