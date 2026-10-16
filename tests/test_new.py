"""Tests for `article-pipeline new` and `article-pipeline status`."""

from __future__ import annotations

from pathlib import Path

from article_pipeline.cli import main
from article_pipeline.run import read_sources


def test_new_scaffolds_brief_sources_and_copies_local_files(tmp_path: Path, capsys) -> None:
    notes = tmp_path / "notes.md"
    notes.write_text("Of the 140 crews surveyed, 87 reported offline hours.\n", encoding="utf-8")
    runs = tmp_path / "runs"

    code = main(
        [
            "new",
            "offline-first",
            "--topic",
            "Why small field teams adopt offline-first apps",
            "--source",
            str(notes),
            "--source",
            "https://example.org/essay",
            "--runs-dir",
            str(runs),
            "--date",
            "2026-10-16",
        ]
    )

    assert code == 0
    run_dir = runs / "2026-10-16-offline-first"
    assert "Created" in capsys.readouterr().out
    assert "Why small field teams adopt offline-first apps" in (run_dir / "brief.md").read_text()
    assert (run_dir / "research").is_dir()
    assert (run_dir / "sources" / "s1-notes.md").read_text() == notes.read_text()

    sources = read_sources(run_dir)
    assert list(sources) == ["S1", "S2"]
    assert sources["S1"].location == "sources/s1-notes.md"
    assert not sources["S1"].is_remote
    assert sources["S2"].is_remote


def test_new_refuses_existing_folder_bad_slug_and_missing_source(tmp_path: Path, capsys) -> None:
    runs = tmp_path / "runs"
    base = ["--topic", "t", "--source", "https://example.org/a", "--runs-dir", str(runs)]

    assert main(["new", "Bad Slug", *base]) == 1
    assert "slug" in capsys.readouterr().err

    assert main(["new", "ok", *base, "--date", "2026-10-16"]) == 0
    assert main(["new", "ok", *base, "--date", "2026-10-16"]) == 1
    assert "already exists" in capsys.readouterr().err

    assert main(["new", "other", "--topic", "t", "--source", str(tmp_path / "gone.md"), "--runs-dir", str(runs)]) == 1
    assert "not found" in capsys.readouterr().err
    assert not (runs / "gone").exists()


def test_status_lists_stages_and_verdict(passing_run: Path, capsys) -> None:
    assert main(["status", str(passing_run)]) == 0
    before = capsys.readouterr().out
    assert "[x] 1 brief" not in before
    assert "[x] 4 draft" in before
    assert "[ ] 5 fact check" in before

    main(["check", str(passing_run)])
    capsys.readouterr()
    main(["status", str(passing_run)])
    after = capsys.readouterr().out
    assert "[x] 5 fact check  factcheck.md (PASS)" in after
