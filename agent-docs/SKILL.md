---
name: agent-docs
description: Use when the user asks to init or bootstrap project or agent docs, create or add a README, CLAUDE.md, or AGENTS.md, add missing doc files, or set up agent instructions, in a project that already has substance to document (code, a requirements or spec doc, a PRD). Do NOT use on a blank or empty project with nothing to derive docs from, and do NOT use to edit, improve, or restructure docs that already exist.
---

# Init Project Docs

Check the project root for README.md, AGENTS.md, and CLAUDE.md. Create whichever are missing. NEVER modify or overwrite one that exists, even partially; if all three exist, say so and stop.

## First: survey the project

Before writing anything, build real understanding. Read the file tree, package manifests and lockfiles, scripts/tasks, CI config, recent git log, and any requirements, spec, or PRD documents (a spec-only repo is a valid and sufficient source; a good PRD answers most README questions and seeds the AGENTS.md core vocabulary and never-compromise list). Skim the main entry points if code exists. Check the project root, and only the root, for a `CONTEXT.md` or equivalent glossary: if one is there, it owns the project's vocabulary and AGENTS.md should point at it rather than restate it. Ignore glossaries in subdirectories; those belong to a package, not the project. Everything you write must be derived from this specific project. Generic boilerplate ("write clean code", "follow best practices") is worse than nothing: delete any sentence that would be true of every repo on earth.

If the survey finds no substantive source material (no code, no requirements/spec/PRD, no meaningful history), STOP. Tell the user there is nothing to derive documentation from yet and that the skill should be run again once the project has a spec or code. Do not create any files in this case; docs invented from nothing are boilerplate by definition.

## README.md (if missing)

Audience: humans, and agents deciding whether to use this project. NOT instructions for working on it.

- What this is and why it exists, in the first two sentences
- Status if relevant (personal tool, experiment, production)
- Quickstart: install, configure, run, in copy-pasteable commands verified against the actual scripts/manifest
- Basic usage
- Pointers to deeper docs if they exist

Keep it short. Do not put contributor/agent instructions here.

## AGENTS.md (if missing)

This is the canonical agent instruction file, read natively by Codex, Cursor, and others, and by Claude Code via the CLAUDE.md import. Audience: agents changing this codebase. It must be incredibly different from the README: not what the project is, but how to work on it and what to know before making changes.

Include, derived from the survey:

- One-line project description, then straight to operational content
- Commands: how to build, test, lint, typecheck, and run, exactly as this repo does it
- Architecture in brief: the main modules/directories and what owns what. Point to deeper docs rather than inlining them
- Conventions actually observable in the code (naming, error handling, file organisation, commit/PR style from git log)
- Core vocabulary: the project-specific terms an agent cannot work without, with one-line definitions. The point is the agent describing things back in the project's own language, not a complete lexicon. If a `CONTEXT.md` exists, link to it and inline only the few terms needed to read the rest of this file. Keep the terms that carry weight inline either way — AGENTS.md is loaded every session and `CONTEXT.md` is not, and agents reading AGENTS.md natively have no import mechanism, so a pointer alone does not put a term in context
- What never to compromise on: the two or three properties that define this project (e.g. "pages render from stored data only", "no network calls at import time"). Changes that hurt these should not be made
- A `## Failure modes` section, initially containing only: "Add bad/good example pairs here as recurring agent mistakes are observed." Do not invent hypothetical examples; these only have value when they encode real observed failures

Keep the whole file tight. It is loaded into every session; every line costs context. No full API docs, no tutorials, no restating the README.

## CLAUDE.md (if missing)

Exactly one line:

@AGENTS.md

This is Claude Code's import syntax; Claude reads AGENTS.md through it. Do not duplicate content here. Claude-specific additions can be appended below the import later, only if a genuine Claude-only need appears.

## Finish

List what was created and what was skipped because it existed. Suggest the user skim AGENTS.md and correct anything that misreads the project; a wrong instruction file is worse than none.

If the project has real domain vocabulary and no `CONTEXT.md`, suggest running `/build-context` to produce the full glossary, and note that the core vocabulary in AGENTS.md can then be trimmed to a pointer plus the terms needed to read the file. Do not run it as part of this skill: it is an interactive process that works through terms one question at a time, and the user should choose when to sit through it.