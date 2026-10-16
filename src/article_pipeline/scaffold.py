"""Create a new run folder with brief.md, sources.md and copied local sources."""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from datetime import date
from pathlib import Path

SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

BRIEF_TEMPLATE = """# Brief

- Topic: {topic}
- Audience: {audience}
- Angle: {angle}
- Voice: plain, direct, short sentences; no marketing words
- Length: 900 to 1,400 words

## Allowed sources

Only the sources listed in `sources.md` may be used. Nothing else, not even
general knowledge, enters the draft as a factual claim.

## Research angles

1. facts-and-figures: numbers, dates, definitions
2. practitioner-experience: what people who did it report
3. counter-arguments-and-limits: where it fails, what the critics say
"""

SOURCES_HEADER = """# Sources

| id | title | location |
|----|-------|----------|
"""


class ScaffoldError(Exception):
    """Raised when a run cannot be created."""


@dataclass(frozen=True)
class NewRun:
    run_dir: Path
    source_ids: list[str]


def run_folder_name(slug: str, on: date | None = None) -> str:
    on = on or date.today()
    return f"{on.isoformat()}-{slug}"


def _title_for(location: str) -> str:
    if location.startswith(("http://", "https://")):
        return location.split("//", 1)[1].rstrip("/")
    return Path(location).stem.replace("-", " ").replace("_", " ")


def create_run(
    slug: str,
    topic: str,
    sources: list[str],
    runs_dir: Path = Path("runs"),
    audience: str = "to be confirmed with the user",
    angle: str = "to be confirmed with the user",
    on: date | None = None,
) -> NewRun:
    """Create `runs/<date>-<slug>/` with brief.md, sources.md and sources/."""
    if not SLUG.match(slug):
        raise ScaffoldError(f"slug must be lowercase words joined by hyphens: {slug!r}")
    if not sources:
        raise ScaffoldError("at least one --source is required")

    run_dir = runs_dir / run_folder_name(slug, on)
    if run_dir.exists():
        raise ScaffoldError(f"run folder already exists: {run_dir}")

    local: list[tuple[str, Path]] = []
    for location in sources:
        if location.startswith(("http://", "https://")):
            continue
        path = Path(location).expanduser()
        if not path.is_file():
            raise ScaffoldError(f"local source not found: {location}")
        local.append((location, path))

    (run_dir / "sources").mkdir(parents=True)
    (run_dir / "research").mkdir()

    rows: list[str] = []
    source_ids: list[str] = []
    local_by_location = dict(local)
    for index, location in enumerate(sources, start=1):
        source_id = f"S{index}"
        source_ids.append(source_id)
        if location in local_by_location:
            original = local_by_location[location]
            target_name = f"{source_id.lower()}-{original.name}"
            shutil.copyfile(original, run_dir / "sources" / target_name)
            stored = f"sources/{target_name}"
        else:
            stored = location
        rows.append(f"| {source_id} | {_title_for(location)} | {stored} |")

    (run_dir / "sources.md").write_text(
        SOURCES_HEADER + "\n".join(rows) + "\n", encoding="utf-8"
    )
    (run_dir / "brief.md").write_text(
        BRIEF_TEMPLATE.format(topic=topic, audience=audience, angle=angle),
        encoding="utf-8",
    )
    return NewRun(run_dir=run_dir, source_ids=source_ids)
