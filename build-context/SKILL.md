---
name: build-context
description: >
  Generate or update a CONTEXT.md file that formalises the domain-specific language for a project — capturing shared terminology used by the codebase, developers, and domain experts. Trigger when the user says "generate a CONTEXT.md", "create a context file", "let's define our domain language", "formalise our terminology", or when a project is already underway and the user wants to capture the vocabulary that has accumulated across conversations, code, and notes. Also trigger when the user says "/build-context" or asks to "capture the language we've been using". Particularly useful mid-project when informal terms have started to solidify into real concepts that need shared definitions.
---

# /build-context

Generates a `CONTEXT.md` — a living glossary that aligns three groups around shared language: the codebase, the developers building it, and the domain experts who understand the problem. When all three speak the same vocabulary, communication becomes precise and the code reflects reality.

Run this at any point in a project. The earlier it's established, the better — but mid-project is fine too. The output is a versioned, editable file that grows with the project.

---

## Process

### 1. Gather context

Before writing anything, collect material from every available source:

**Conversation history**
Scan the current conversation (and search past conversations if the tool is available) for:
- Named concepts, entities, or things that are referred to consistently
- Terms that appear in quotes or with implicit special meaning ("the funnel", "a click", "a subscriber")
- Any place where a term was clarified or corrected mid-conversation
- Phrases that sound domain-specific but were never formally defined

**Memory**
Check the user's memory for project-specific context — stack names, system names, company structure, role descriptions, known domain vocabulary.

**Notes and files**
If file access is available, look for:
- Any existing glossary, README, or CONTEXT.md
- Project notes that use domain terms
- Specification documents or briefs

**Codebase**
If a codebase is accessible (via file tools, GitHub MCP, or uploads):
- Scan function names, variable names, route names, database column names
- Look for model/entity names (these are almost always domain terms)
- Note any naming inconsistencies — two names for the same thing is a red flag worth surfacing

---

### 2. Draft the term list

From everything gathered, extract a candidate list of terms. Aim to cover:

- **Core entities** — the main nouns the system operates on (e.g. Order, Subscriber, Article)
- **Actions and events** — what happens in the system (e.g. Subscribe, Renew, Click)
- **Roles and actors** — who uses the system (e.g. Reader, Editor, Admin)
- **System concepts** — internal architecture terms that have become shared vocabulary (e.g. Funnel, Pipeline, Shortlink)
- **Boundary terms** — places where the team's language diverges from the domain expert's, or where two valid words exist for the same thing

For each term, attempt a one-to-two sentence definition and a list of terms to avoid.

---

### 3. Clarify and confirm

Before writing the final CONTEXT.md, surface any uncertainties. Work through them one question at a time — do not dump a list of questions on the user.

**Terms that need clarification** (things gathered but not well-defined):
Ask the user directly, and always include a recommended definition as a starting point. Format:

> "I picked up the term **Subscriber** throughout the conversation, but it's not fully defined. I'd suggest: *A person with an active paid or trial subscription to the publication.* Does that sound right, or would you adjust it?"

**Terms that seem missing** (concepts implied but not named):
If there's a clear concept operating in the project that hasn't been named, suggest it. Format:

> "There seems to be a concept of a *lapsed subscriber* — someone whose subscription has expired but who hasn't cancelled. It might be worth naming and defining that explicitly. Want to include it?"

Ask one question at a time. Wait for a response before moving to the next. Continue until:
- All gathered terms are confirmed or discarded
- Any suggested additions are accepted or declined
- No major concept feels like it's floating without a name

---

### 4. Write the CONTEXT.md

Once terms are confirmed, produce the file using this exact format:

```markdown
# {Context Name}
{One or two sentence description of what this context is and why it exists.}

## Language

**{Term}**:
{One or two sentence definition. Precise and plain. Avoid implementation detail unless it's essential to the definition.}
_Avoid_: {comma-separated list of synonyms or near-synonyms to retire}
```

**Ordering**: Alphabetical within the Language section, unless there's a strong reason to group related terms (e.g. a cluster of financial terms, or a cluster of user-role terms). If grouped, add a brief subheading.

**Definitions should**:
- Be readable by a non-technical domain expert
- Be precise enough that a developer could name a function or table column from it
- Avoid circular definitions ("A subscriber is someone who has subscribed")
- Not contain implementation detail unless it's unavoidable (e.g. "stored as a Unix timestamp" is usually irrelevant)

**Avoid lists should**:
- Name real alternatives that appear in the wild (in code, in conversation, in the domain)
- Not pad out with every possible synonym — only the ones that actually cause confusion

---

### 5. Present and package

- If file tools are avaible then add it to the root of the curent project, otherwise produce the CONTEXT.md as a downloadable file
- Briefly summarise what was captured: how many terms, any key decisions made during clarification
- Note any terms that were deferred or need a follow-up (e.g. "We didn't nail down a definition for 'Reader' vs 'User' — worth revisiting")
- Suggest the file lives at the root of the project repo, or alongside a README

---

## Notes

- If the project has an existing CONTEXT.md, read it first and treat the task as an update: preserve existing entries, extend or refine where the conversation has evolved them, and add newly emerged terms.
- If a term appears in code under one name and in conversation under another, flag the discrepancy explicitly rather than silently picking one. This is usually the most valuable output.
- Domain experts define meaning; developers define implementation. A CONTEXT.md entry should reflect domain meaning first. If the implementation diverges, note it but don't let it drive the definition.
- Keep entries tight. A CONTEXT.md that bloats into a full technical spec stops being useful as shared language. If a term needs more than two sentences, it probably needs a separate document linked from here.