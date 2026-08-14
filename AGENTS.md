# NiceSkills agent instructions

This repository contains small, self-contained Codex skills, one directory per skill.

## Source of truth

**When creating or editing a skill in collaboration with the user, always work on the version in this repository. Never edit the copy installed in the currently active agent.**

Installed skill copies are runtime artifacts and may be stale or replaced. Treat `<repo>/<skill-name>/` as the editable source. Installation or cache refresh is a separate, explicit step.

## Working in this repository

- Read the target skill's complete `SKILL.md` before changing it.
- Keep each skill self-contained. Put supporting material under that skill's `scripts/`, `references/`, or `assets/` directory.
- Preserve YAML frontmatter with a concise `name` and trigger-focused `description`.
- Follow the existing direct, procedural Markdown style. Keep instructions specific enough for an agent to execute.
- Do not modify unrelated skills or user-owned worktree changes.

## Verification

There is no repo-wide build, test, lint, or typecheck command. Review the changed Markdown and diff directly. For a skill with scripts, run the smallest relevant script-level check available.

## Repository map

- `<skill-name>/SKILL.md`: canonical skill definition and workflow.
- `<skill-name>/scripts/`: executable helpers owned by that skill.
- `<skill-name>/references/`: supporting detail loaded only when relevant.
- `README.md`: human-facing catalogue of the skills.

## Glossary

- **Repository copy**: canonical editable version of a skill in this project.
- **Installed copy**: version loaded into an active agent environment; never the editing target.
- **Skill**: a directory whose `SKILL.md` defines triggers and operating instructions.

## Never compromise

- Edit the repository copy, never the active agent's installed copy.
- Keep skills focused and self-contained.
- Preserve unrelated worktree changes.

## Failure modes

Add bad/good example pairs here as recurring agent mistakes are observed.
