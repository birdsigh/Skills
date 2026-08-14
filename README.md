<p>
  <a href="https://sprettynice.com">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://sprettynice.com/github/img/logo-light.png">
      <source media="(prefers-color-scheme: light)" srcset="https://sprettynice.com/github/img/logo-dark.png">
      <img alt="NiceSkills" src="https://sprettynice.com/github/img/logo-dark.png" width="220">
    </picture>
  </a>
</p>

[![skills.sh](https://skills.sh/b/birdsigh/skills)](https://skills.sh/birdsigh/skills)

<p align="center">Small, focused skills written to meet ad-hoc needs. Each one is self-contained and adaptable.</p>

## Installation

```bash
npx skills@latest add birdsigh/skills
```

## NiceSkills

**[build-context](build-context/)** — Generates a `CONTEXT.md` glossary that aligns a codebase, its developers, and domain experts around shared language. Run it at any point in a green- or brown-field project to formalise the vocabulary that's accumulated in conversation and code. Inspired by the usage of context files in the excellent skills [by Matt Pocock](https://github.com/mattpocock/skills).

In any project that involves an AI, you spend tokens re-explaining jargon every session. "The funnel" means something specific in your product, "a subscriber" has a precise definition your team argues about, "materialization" is a term of art that took months to coin. Without a shared glossary, the AI guesses — uses 20 words where 1 would do, names things inconsistently, misses the nuance domain experts take for granted. A formalised context document pays for itself within a few sessions.

It and `agent-docs` know about each other. A vocabulary section in an existing AGENTS.md is treated as a seed list rather than rediscovered from scratch, and once the `CONTEXT.md` is written the skill offers to trim that section back to a pointer so the same terms aren't left drifting in two files. Run them in either order.

**[agent-docs](agent-docs/)** — Writes the missing `README.md`, `AGENTS.md`, and `CLAUDE.md` for a project that already has something to document — code, a spec, a PRD. It surveys the project first and derives every line from what it finds, and it never touches a file that already exists.

Docs often arrive by accident: a README written on day one and never revisited, an AGENTS.md pasted in from another repo. What you get is boilerplate that would be true of any repo on earth, which is worse than nothing once it's loaded into every session. The split is the useful part — README for people deciding whether to use the thing, AGENTS.md for agents changing it, CLAUDE.md as a one-line import so there's a single canonical source instead of three copies drifting apart. The handoff to `build-context` above follows the same principle. And if the project has no real source material yet, the skill refuses to write anything, on the grounds that docs invented from nothing are the problem it exists to avoid.

**[commit-and-push](commit-and-push/)** — Reviews, verifies, commits, and pushes a repository's intended changes without disturbing unrelated work. It audits existing outgoing commits, requires a configured upstream, and asks for explicit confirmation immediately before every push.

Publishing local work should be boring, but a casual `git add . && git push` quietly bundles unrelated edits, stale outgoing commits, generated files, or the wrong destination. This skill turns that boundary into a deliberate review: fetch first, account for every changed path, preserve user-owned staging, run focused checks, and show the complete push before anything leaves the machine. It never force-pushes or reconciles a diverged branch on the user's behalf.

**[be-concise](be-concise/)** — Tells the model to give answers, not essays: sacrifice grammar for concision where it doesn't cost critical detail. Invoke it mid-session when you're deep in back-and-forth debugging and every reply is arriving wrapped in three paragraphs of preamble.

The skill itself is one sentence, which is the point. Verbosity compounds: long replies fill the context window, which degrades later output, which invites more back-and-forth. A standing instruction to compress is cheaper than editing every prompt to say "briefly".

**[deploy-prototype](deploy-prototype/)** — Deploys static HTML prototypes to a [ProtoLab](https://github.com/birdsigh/ProtoLab) instance (a Cloudflare Worker that hosts throwaway prototypes) with one command, via a bundled Python client that handles pairing, lab selection, zipping, and error messages. Also manages the lab itself: listing and switching labs, removing prototypes, health checks.

The gap between "I built a prototype" and "here's a link you can open on your phone" is bigger than it should be. Real hosting (repos, wrangler, build pipelines) is overkill for something that might live for a day, but screenshots and screen shares undersell interactive work. This skill makes the deploy a single authenticated HTTP call, with guardrails where they matter: it always confirms the deploy plan before shipping (deploys overwrite by slug), and refuses anything that needs a backend or build step rather than quietly producing a broken approximation.

**[response-analysis](response-analysis/)** — Scores qualitative responses (interviews, surveys, support tickets) on sentiment, pain level, and excitement about a solution. Each score is backed by verbatim quotes from the source.

Qualitative feedback is hard to act on at scale. Anyone who's done user research knows the feeling, you have 20 interview transcripts and a stakeholder asking "so what do people think?" The temptation is to pattern-match on memorable quotes and call it insight. This skill forces evidence-backed scoring so gut feeling cannot masquerade as analysis. The three dimensions are also deliberately separate: a frustrated customer can be genuinely excited about a fix, and conflating the two is how bad product decisions get made.

## Session hygiene

`wind-down`, `wrap-up`, and `suggest-next` were designed together as a session-closing system, growing out of a conversation about the structural parallel between AI context degradation and human cognitive fatigue.

The observation that prompted them: the longer a session runs, the worse the output — for the same reason that human cognition degrades past a certain point of wakefulness. Both involve a fixed resource filling up, with quality degrading first in tasks that require integrating disparate information. The key difference is that human fatigue is thermodynamic (genuine exhaustion), while AI degradation is attentional — a recency bias problem rather than depletion.

Sleep's consolidation function — compressing noisy episodic data into denser semantic signal — maps closely onto what a good session close should do: produce a clean, dense handoff rather than leaving continuity to inference. Most people treat chat closure as nothing, when it's actually a transition that benefits from deliberate ritual. Consistent wind-downs improve memory quality by providing that signal explicitly.

**[wind-down](wind-down/)** — Closing summary for informal or exploratory conversations. Captures key ideas, open questions, and things worth sitting with. The equivalent of writing up notes before sleep.

**[wrap-up](wrap-up/)** — Closing summary for work sessions. Documents what was built, what wasn't, and what comes next — precise enough to resume cold.

**[suggest-next](suggest-next/)** — Surfaces follow-on ideas, tasks, and reading after a session wraps up. Detects whether the session was exploratory or work-focused and adjusts suggestions accordingly.
