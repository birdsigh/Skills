# NiceSkills

Small, focused skills written to meet ad-hoc needs. Each one is self-contained and adaptable — drop them into any Claude setup.

## Skills

**[build-context](build-context/)** — Generates a `CONTEXT.md` glossary that aligns a codebase, its developers, and domain experts around shared language. Run it at any point in a project to formalise the vocabulary that's accumulated in conversation and code. Inspired by the usage of context files in the excellent skills [by Matt Pocock](https://github.com/mattpocock/skills).

**[response-analysis](response-analysis/)** — Scores qualitative responses (interviews, surveys, support tickets) on sentiment, pain level, and excitement about a solution. Each score is backed by verbatim quotes from the source.

## Session hygiene

`wind-down`, `wrap-up`, and `suggest-next` were designed together as a session-closing system, growing out of a conversation about the structural parallel between AI context degradation and human cognitive fatigue.

The observation that prompted them: the longer a session runs, the worse the output — for the same reason that human cognition degrades past a certain point of wakefulness. Both involve a fixed resource filling up, with quality degrading first in tasks that require integrating disparate information. The key difference is that human fatigue is thermodynamic (genuine exhaustion), while AI degradation is attentional — a recency bias problem rather than depletion.

Sleep's consolidation function — compressing noisy episodic data into denser semantic signal — maps closely onto what a good session close should do: produce a clean, dense handoff rather than leaving continuity to inference. Most people treat chat closure as nothing, when it's actually a transition that benefits from deliberate ritual. Consistent wind-downs improve memory quality by providing that signal explicitly.

**[wind-down](wind-down/)** — Closing summary for informal or exploratory conversations. Captures key ideas, open questions, and things worth sitting with. The equivalent of writing up notes before sleep.

**[wrap-up](wrap-up/)** — Closing summary for work sessions. Documents what was built, what wasn't, and what comes next — precise enough to resume cold.

**[suggest-next](suggest-next/)** — Surfaces follow-on ideas, tasks, and reading after a session wraps up. Detects whether the session was exploratory or work-focused and adjusts suggestions accordingly.
