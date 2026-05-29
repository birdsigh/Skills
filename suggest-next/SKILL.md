---
name: suggest-next
description: >
  Surface related ideas, tasks, reading, and follow-on conversations based on what was just discussed or built. Trigger whenever the user types /suggest-next, or after completing a /wind-down or /wrap-up when further suggestions would add value. Also trigger when the user asks things like "what else could we do", "any related ideas?", "what should I look into next?", or "what are we missing?". Automatically detects whether the session was work-focused or exploratory and adjusts suggestions accordingly — no need for the user to specify.
---
 
# /suggest-next
 
Seeds future conversations and tasks by surfacing what the current session implies but didn't cover. The goal is to plant ideas that will benefit from being "slept on" — things the user might want to return to, explore further, or act on in a future session.
 
This is generative and lateral, not administrative. It's not a task list or a project management tool — it's more like a well-read colleague saying "oh, while we're on this topic, have you thought about..."
 
## Context detection
 
Before writing, determine which mode applies based on the conversation:
 
**Exploratory mode** — the session was a discussion, brainstorm, research dive, or conceptual conversation. Suggestions lean toward: related ideas and concepts, books and articles, rabbit holes worth exploring, questions worth sitting with, future conversations to have.
 
**Work mode** — the session involved building, fixing, or shipping something. Suggestions lean toward: related tasks and improvements, adjacent technical concerns, relevant tools or libraries, recent news or developments in the tech area worked in, further learning directly applicable to the work.
 
Many sessions will mix both — surface suggestions from both modes where relevant, but weight toward whichever dominated.
 
## Output structure
 
---
 
### 💡 Suggest Next: [Short title echoing the session's theme]
 
**If you want to go deeper**
Ideas, topics, or questions that extend directly from what was discussed or built. These are the natural "next chapter" — not tangents, but continuations. 2–4 items, each with a sentence of context explaining the connection.
 
**Related things worth exploring**
Lateral suggestions — adjacent topics, alternative approaches, contrasting perspectives. Things that aren't a direct continuation but are meaningfully connected and would enrich understanding or expand the work. 2–4 items.
 
**Worth reading / watching / listening to**
Specific recommendations — books, articles, talks, podcasts, documentation — that are directly relevant to what came up. Be specific: title, author/source, and one sentence on why it's relevant here. Omit vague genre suggestions ("you might enjoy books about AI"). Only include if genuinely relevant recommendations exist.
 
**Tasks this session implies** *(work mode only)*
Concrete tasks that weren't in scope for this session but are clearly implied by it. Framed as actionable items, specific enough to become a ticket or task. Omit in exploratory mode.
 
**Loose thread...**
One single observation, question, or provocation to carry forward — something that didn't get proper attention this session but deserves to be the starting point of a future one. This should feel like a good conversation ender: something worth sitting with.
 
---
 
## Notes for execution
 
- Read the full conversation before writing, not just the wind-down or wrap-up output. The best suggestions often come from things mentioned in passing that didn't get developed.
- Be specific. "You might enjoy reading about cognitive science" is useless. "You might enjoy 'Why We Sleep' by Matthew Walker — it covers the memory consolidation mechanisms we touched on, with the research behind them" is useful.
- For work mode, check whether there are obvious related concerns the session didn't address — performance, accessibility, security, testing, documentation — and surface whichever are genuinely relevant rather than running through a checklist.
- The "Loose thread..." section is the most important one. It should feel like a gift, not a chore — something that makes the user think "yes, I want to come back to that."
- Don't pad. Three strong suggestions beat six weak ones. Omit any section where nothing genuinely good comes to mind.
- If web search is available and the session touched on recent tech, tools, or current events, consider searching for recent relevant news or developments to surface in suggestions.
