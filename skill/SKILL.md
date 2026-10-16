---
name: article-pipeline
description: Produce a long-form article from a fixed list of verified sources. Three research subagents in parallel, one writer, then a deterministic fact-check gate. Use when the user asks for an article, a long post, or a white paper that must be sourced. Output is a proposal folder for a person to review; nothing is published.
---

# article-pipeline

You turn a brief and a list of allowed sources into a draft article with a
citation after every factual sentence, and a fact-check report that says PASS.
You work inside one run folder and never outside it.

## Before you start

- CLI: `article-pipeline`. If it is not on PATH, use
  `uv run --project <path-to-clone> article-pipeline` with the path from the
  skill README. Every CLI call below means this command.
- Run folder: `runs/<date>-<slug>/`, created by `article-pipeline new`. All
  paths below are relative to it.
- Allowed sources are the rows of `sources.md` and nothing else. No web search,
  no memory, no general knowledge enters the draft as a factual claim.
- Keep a task list with the six steps below and tick them as you go.

## Step 1: brief

Ask the user for anything missing: topic, audience, angle, voice, and the
sources (URLs or local files). Then run:

    article-pipeline new <slug> --topic "<topic>" --source <url-or-path> [--source ...] [--audience "..."] [--angle "..."]

Read `brief.md` and `sources.md`. If audience or angle still say "to be
confirmed", ask, then edit `brief.md`. Do not continue with a vague brief.

## Step 2: research, in parallel

Spawn three subagents at the same time, one per angle:

1. `facts-and-figures`: numbers, dates, definitions
2. `practitioner-experience`: what people who did it report
3. `counter-arguments-and-limits`: where it fails, what the critics say

Give each subagent this prompt, with the placeholders filled in:

> You are researching one angle for an article. Angle: `<angle>`. Read
> `brief.md` and `sources.md` in `<run folder>`. You may read only the sources
> listed there: local files under `sources/`, or the URLs given, fetched once.
> Do not search the web. Do not use anything you already know.
> Write `research/<angle>.md`: a heading, one line on which sources you used,
> then a bullet list of claims. Each claim has three sub-bullets:
> `Claim:` one sentence in your words, `Source:` the id in brackets such as
> `[S2]`, `Quote:` a verbatim passage from that source, copied exactly, in
> double quotes, on one line. Twelve claims at most. If a source says nothing
> about your angle, say so and move on. Do not write prose.

Wait for all three. Check that each file exists and that every `Source:` names
an id from `sources.md`. If a subagent used anything outside the sources, drop
those claims.

## Step 3: merge

Do this yourself; it is short. Read the three research files and write
`claims.md`: a heading, one line on how you merged, then one block per claim:

    ## C1
    - Claim: <one sentence>
    - Source: [S1]
    - Quote: "<verbatim passage, one line>"

Drop duplicates. When two sources make the same point, keep the one with the
figure or the direct quote. Number the claims in the order the article will
likely use them. Keep quotes verbatim; the gate checks them letter for letter,
ignoring only case and whitespace.

## Step 4: write, one writer

Spawn one subagent with this prompt:

> Write `draft.md` in `<run folder>`. Read `brief.md` for topic, audience,
> angle, voice and length. Read `claims.md`. Use nothing else. Every factual
> sentence ends with the source id in brackets, for example `[S1]`, placed
> after the period or just before it. A sentence that carries a number, a
> percentage, a year, or a name must have a citation. Sentences with no
> citation may only carry opinion, transition or structure. Do not invent
> figures, names or quotes. Do not write about the sources as sources unless
> the brief asks for it. Markdown with a title and section headings. Match the
> voice in the brief; short sentences, no marketing words.

## Step 5: fact-check gate

Run:

    article-pipeline check runs/<date>-<slug>

The gate is deterministic and does not call a model. It checks that every
`[S#]` in `draft.md` exists in `sources.md`; that every sentence with a number,
a percentage, a year, or a capitalized word that is not the first word has a
citation; and that every quote in `claims.md` appears in its local source file.
It writes `factcheck.md` and exits 1 on FAIL.

On FAIL, read the problems. Fix the draft (add a citation, remove the figure,
rephrase) or fix `claims.md` (correct the quote, drop the claim). Then run the
check again. Repeat until PASS. Never deliver a FAIL. Never edit `factcheck.md`
by hand. Never weaken a quote to make it match.

## Step 6: hand over the proposal

Run `article-pipeline status runs/<date>-<slug>` and show the output. Tell the
user where `draft.md` and `factcheck.md` are, how many claims and citations
there are, and anything the sources did not support that the brief asked for.
The person reads the draft and decides what happens next.

This skill never posts, publishes, emails or uploads anything anywhere; the
output is a folder for a person to review.
