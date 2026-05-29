---
name: wind-down
description: >
  Produce a structured closing summary for informal or exploratory conversations — discussions, brainstorms, research dives, or any chat that isn't primarily a work task. Trigger whenever the user types /wind-down, or says something like "let's wind down", "wrap this up", "summarise what we discussed", or "close out this conversation". Also trigger at the natural end of a long informal chat when the user signals they're done. Do NOT use for task/work completion — use /wrap-up for that instead.
---
 
# /wind-down
 
Produces a warm, well-structured closing summary for informal and exploratory conversations. Think of it as the consolidation layer — the equivalent of writing up notes before sleep, so ideas can be mulled over and returned to later.
 
## Tone
 
Conversational but considered. This isn't a corporate debrief — it's more like a thoughtful friend summarising a good conversation. Avoid bullet-point overload; use prose where it flows better, lists where structure genuinely helps.
 
## Output Structure
 
Produce the following sections. Omit any section that has nothing meaningful to put in it — don't force content.
 
---
 
### 🌙 Wind-Down: [Short evocative title capturing the conversation's essence]
 
**What we explored**
2–4 sentences summarising the arc of the conversation. What was the central question or theme? Where did it go? What shifted or developed as the discussion progressed?
 
**Key ideas and insights**
The most interesting, useful, or novel points that emerged. These should be the things worth remembering — not a transcript, but the signal. Use a short list or prose depending on what suits the content. Aim for 3–6 items.
 
**Things to sit with**
Open questions, unresolved tensions, or ideas that deserve more thought. The "sleep on it" section. Framed as prompts for reflection rather than problems to solve. 2–4 items.
 
**References and rabbit holes**
Any books, articles, tools, concepts, people, or links that came up or were implied. Include brief context for each — why it's relevant to what was discussed. Omit if nothing specific came up.
 
**Possible next steps or follow-ons**
Concrete things that could come next, if any emerged naturally — further conversations, things to try, things to read or watch. Keep this light; this is not a task list. If nothing obvious emerged, omit this section.
 
---
 
## Notes for execution
 
- Read back through the full conversation before writing. Don't rely on recency bias — earlier parts of long conversations often contain the most interesting material.
- The title should feel earned, not generic. "Wind-Down: AI and Cognition" is lazy. "Wind-Down: Sleep Hygiene for Machines" is better.
- "Things to sit with" is the most valuable section for many conversations — don't skip it or phone it in.
- If the conversation touched on personal context (the user's work, projects, interests), reflect that back specifically rather than speaking generically.
- After completing the wind-down, consider whether to invoke /suggest-next to surface related ideas, tasks, or reading for the user to consider.
