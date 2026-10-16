"""Report which stages of a run exist."""

from __future__ import annotations

import re
from pathlib import Path

RESULT = re.compile(r"^Result:\s*(PASS|FAIL)\s*$", re.MULTILINE)


def factcheck_result(run_dir: Path) -> str | None:
    path = run_dir / "factcheck.md"
    if not path.is_file():
        return None
    match = RESULT.search(path.read_text(encoding="utf-8"))
    return match.group(1) if match else "unknown"


def status_lines(run_dir: Path) -> list[str]:
    """One line per stage, in pipeline order."""

    def mark(present: bool) -> str:
        return "[x]" if present else "[ ]"

    research_files = sorted((run_dir / "research").glob("*.md")) if (
        run_dir / "research"
    ).is_dir() else []
    source_files = sorted((run_dir / "sources").glob("*")) if (
        run_dir / "sources"
    ).is_dir() else []
    verdict = factcheck_result(run_dir)

    lines = [
        f"{mark((run_dir / 'brief.md').is_file())} 1 brief       brief.md",
        f"{mark((run_dir / 'sources.md').is_file())} 1 sources     sources.md "
        f"({len(source_files)} local file{'s' if len(source_files) != 1 else ''})",
        f"{mark(bool(research_files))} 2 research    research/ "
        f"({len(research_files)} file{'s' if len(research_files) != 1 else ''})",
        f"{mark((run_dir / 'claims.md').is_file())} 3 merge       claims.md",
        f"{mark((run_dir / 'draft.md').is_file())} 4 draft       draft.md",
        f"{mark(verdict is not None)} 5 fact check  factcheck.md"
        + (f" ({verdict})" if verdict else ""),
    ]
    return lines
