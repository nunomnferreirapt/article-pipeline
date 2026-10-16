"""Command-line entry point: `article-pipeline new | check | status`."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from . import __version__
from .check import check_and_write
from .scaffold import ScaffoldError, create_run
from .status import status_lines


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="article-pipeline",
        description=(
            "Long-form articles from verified sources. The CLI scaffolds a run, "
            "reports its stages, and runs the fact-check gate. It never publishes."
        ),
    )
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)

    new = commands.add_parser("new", help="create runs/<date>-<slug>/ with brief and sources")
    new.add_argument("slug", help="lowercase words joined by hyphens")
    new.add_argument("--topic", required=True, help="what the article is about")
    new.add_argument(
        "--source",
        action="append",
        default=[],
        metavar="URL_OR_PATH",
        help="an allowed source; repeat for each one. Local files are copied in.",
    )
    new.add_argument("--audience", default="to be confirmed with the user")
    new.add_argument("--angle", default="to be confirmed with the user")
    new.add_argument("--runs-dir", type=Path, default=Path("runs"))
    new.add_argument("--date", type=date.fromisoformat, default=None, help="YYYY-MM-DD")

    check = commands.add_parser("check", help="run the fact-check gate on a run folder")
    check.add_argument("run_dir", type=Path)

    status = commands.add_parser("status", help="show which stages of a run exist")
    status.add_argument("run_dir", type=Path)
    return parser


def cmd_new(args: argparse.Namespace) -> int:
    try:
        result = create_run(
            slug=args.slug,
            topic=args.topic,
            sources=args.source,
            runs_dir=args.runs_dir,
            audience=args.audience,
            angle=args.angle,
            on=args.date,
        )
    except ScaffoldError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"Created {result.run_dir}/")
    print(f"  brief.md      topic: {args.topic}")
    print(f"  sources.md    {len(result.source_ids)} source(s): {', '.join(result.source_ids)}")
    print("Next: fill in audience and angle in brief.md, then run the skill.")
    return 0


def _require_run_dir(run_dir: Path) -> bool:
    if run_dir.is_dir():
        return True
    print(f"error: not a run folder: {run_dir}", file=sys.stderr)
    return False


def cmd_check(args: argparse.Namespace) -> int:
    if not _require_run_dir(args.run_dir):
        return 1
    report = check_and_write(args.run_dir)
    print(f"{report.verdict}  {args.run_dir}/factcheck.md")
    print(f"  sentences: {report.sentences} ({report.cited_sentences} cited)")
    print(
        f"  claims: {report.claims} ({report.verified_quotes} quotes verified, "
        f"{report.skipped_remote_quotes} remote not fetched)"
    )
    if report.problems:
        print(f"  problems: {len(report.problems)}")
        for problem in report.problems:
            print(f"  - {problem}")
        return 1
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    if not _require_run_dir(args.run_dir):
        return 1
    print(f"{args.run_dir}/")
    for line in status_lines(args.run_dir):
        print(f"  {line}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    handlers = {"new": cmd_new, "check": cmd_check, "status": cmd_status}
    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
