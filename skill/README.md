# Installing the skill

The skill is the folder next to this file. Claude Code reads `SKILL.md` and
follows it when you type `/article-pipeline` or ask for a sourced article.

## 1. Put the CLI somewhere Claude Code can run it

From the root of this repository:

    uv sync

This creates a project-local virtual environment with the `article-pipeline`
command inside it. Nothing is installed globally. Two ways to make it callable:

- Keep the clone where it is and run the CLI as
  `uv run --project /path/to/article-pipeline article-pipeline ...`.
  Edit the "Before you start" section of `SKILL.md` and put that path in.
- Or activate the environment (`source .venv/bin/activate`) in the shell where
  you start Claude Code, so `article-pipeline` is on PATH.

## 2. Copy the skill folder

    mkdir -p ~/.claude/skills
    cp -R skill ~/.claude/skills/article-pipeline

For one project only, copy it to `<project>/.claude/skills/article-pipeline`
instead.

## 3. Check it is picked up

Start Claude Code in a folder where you want runs to live and type
`/article-pipeline`. Claude Code should ask for a topic and sources, or read
them from your message, then create `runs/<date>-<slug>/`.

## Updating

Pull the repository, run `uv sync`, and copy the `skill` folder again.

## Removing

    rm -r ~/.claude/skills/article-pipeline

Delete the clone to remove the CLI and its environment.
