---
name: wrap-up
description: >
  Produce a structured closing summary for work-focused sessions — coding tasks, feature builds, bug fixes, design work, content production, or any session with a defined goal or deliverable. Trigger whenever the user types /wrap-up, or says something like "let's wrap up", "we're done with this task", "summarise what we built", or "what did we get done". Also trigger when a task reaches a natural completion point and the user signals they want to review what was accomplished. Do NOT use for informal chats or exploratory discussions — use /wind-down for those instead.
---
 
# /wrap-up
 
Produces a clear, honest closing summary for work sessions. The goal is to give both the user and any future session a complete picture of what was done, how it compares to what was intended, and what comes next. Think of it as the handover document — precise enough to resume work cold, honest enough to flag what didn't get done.
 
## Tone
 
Professional but not stiff. Direct and accurate. This isn't a celebration or a post-mortem — it's a clear-eyed account of where things landed. Flag incomplete items plainly without over-explaining.
 
## Before writing
 
Scan the full conversation for:
- Any spec, PRD, brief, or stated goals at the outset
- Any checkpoints, waypoints, or milestones that were set
- What was actually built, written, fixed, or decided
- Any blockers, diversions, or scope changes that occurred
- Any explicit TODOs, known issues, or deferred items mentioned
If no formal spec exists, infer the intended goal from the opening of the conversation.
 
## Output Structure
 
Produce the following sections. Omit any section that has nothing meaningful to put in it.
 
---
 
### ✅ Wrap-Up: [Brief descriptive title — what was built or done]
 
**Goal**
One or two sentences stating what this session set out to accomplish, based on the spec, PRD, or stated intent at the outset. If goals evolved during the session, note that briefly.
 
**What was done**
A clear account of what was actually accomplished versus what was intended. Be specific — reference file names, features, decisions, outputs where relevant. If explicit checkpoints or acceptance criteria were set at the outset, review each one here: was it met, partially met, or skipped, and why? If no formal checkpoints exist, a single honest account of what was done versus the stated goal is sufficient.
 
**What wasn't completed**
Anything that was in scope but didn't get done — deferred, blocked, or deprioritised. Be plain about it. Include brief context if it's useful (why it was deferred, what's needed to unblock it).
 
Omit if everything in scope was completed.
 
**Known issues and open questions**
Bugs, rough edges, unresolved decisions, or things that need a second look. Distinct from "not completed" — these are things that exist in the current output but may need attention.
 
Omit if there are none.
 
**Next steps**
The concrete actions that should follow from this session — ordered by priority where obvious. These should be specific enough to act on: not "improve the UI" but "add loading state to the submit button" or "write tests for the auth module".
 
**References**
A list of any external resources directly relevant to this session — formatted like references in a formal paper. Include where applicable:
- Tickets and issues (Linear, Jira, GitHub Issues, Trello, etc.) — title and URL
- Pull requests — title, number, and URL
- Repositories — name and URL
- Any other directly relevant links (staging URLs, docs, design files, etc.)
Omit if no external references were mentioned or used.
 
---
 
## Notes for execution
 
- Read back through the full conversation before writing. Don't reconstruct from memory of recent messages — the spec or goals are often set early and easy to miss.
- Be honest about what wasn't done. A wrap-up that only lists completions and buries gaps is less useful than one that's accurate.
- "Next steps" should be written as if handed to someone picking this up cold — specific enough to act on without needing to re-read the whole conversation.
- If the session involved multiple distinct workstreams or tasks, structure "What was completed" and "Next steps" accordingly.
- After completing the wrap-up, consider whether to invoke /suggest-next to surface related tasks, improvements, or follow-on work the user might not have considered.
