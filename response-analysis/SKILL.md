---
name: response-analysis
description: Score user-research responses on sentiment, pain, and excitement with quote-backed evidence. Use this whenever the user wants to analyse interview answers, survey responses, support tickets, sales-call transcripts, customer feedback, or any qualitative response on the three dimensions of sentiment, pain level, and excitement about a solution. Trigger on phrases like "analyse this response", "score this interview", "how does this customer feel", "rate the pain level", "extract sentiment", or when the user pastes a transcript and asks for structured emotional/attitudinal analysis. Use even if only one of the three dimensions is mentioned by name.
---

# Response Analysis

Score qualitative responses on three dimensions, each backed by direct quotes from the source. Built for user research, customer interviews, and feedback triage where evidence-backed scoring matters more than vibes.

## Dimensions

Score each on a 1–5 scale. Definitions are deliberately concrete so scores stay consistent across runs.

**Sentiment** — overall emotional tone toward the topic being discussed.
- 1: Strongly negative (frustrated, angry, dismissive)
- 2: Mostly negative (disappointed, sceptical)
- 3: Neutral or mixed
- 4: Mostly positive (interested, satisfied)
- 5: Strongly positive (enthusiastic, delighted)

**Pain level** — intensity of the problem or friction the respondent is experiencing.
- 1: No pain mentioned, or trivial
- 2: Minor annoyance
- 3: Real problem, has workarounds
- 4: Significant pain, actively seeking relief
- 5: Severe, blocking, or recurring pain

**Excitement about solution** — how strongly the respondent reacts to a proposed solution, product, or idea.
- 1: Rejecting or dismissive
- 2: Sceptical or lukewarm
- 3: Curious but uncommitted
- 4: Genuinely interested, would try it
- 5: Enthusiastic, would adopt or pay

## Evidence rules

Every score needs 3 direct quotes from the source that justify it. Quotes must be verbatim — copied character-for-character, no paraphrasing, no tidying up filler words. If the source has fewer than 3 supporting quotes, provide what's there and flag the gap.

**Low-confidence flag.** Mark a score as low-confidence (append `⚠️`) when any of these apply:
- Fewer than 3 supporting quotes exist
- Quotes are ambiguous or could support multiple scores
- The dimension isn't really addressed in the source (e.g. no solution was proposed, so excitement can't be scored fairly)
- The respondent contradicts themselves across the source

When a dimension genuinely doesn't apply, score it `N/A` rather than guessing. Don't pad with weak quotes to hit three.

## Input shapes

The skill handles three input shapes. Detect which one applies from context.

**Single response** — one answer, one ticket, one paragraph. Run the analysis once.

**Full transcript** — multi-turn interview, sales call, or conversation. Analyse the respondent's contributions as a whole, ignoring interviewer turns except as context. If the respondent shifts position mid-transcript, note it.

**Batch** — multiple responses to analyse together. Produce one table per response, each with its own ID or label. If the user wants an aggregate, add a roll-up at the end (mean scores, common themes) but always show the per-response tables first.

If the input shape is genuinely ambiguous, ask once before running. Otherwise proceed.

## Output format

Always use this exact structure. Markdown table for the scores, quoted block for evidence.

```markdown
## Response analysis[: <label if batch>]

| Dimension | Score | Confidence |
|---|---|---|
| Sentiment | <1–5 or N/A> | <high / low ⚠️> |
| Pain level | <1–5 or N/A> | <high / low ⚠️> |
| Excitement about solution | <1–5 or N/A> | <high / low ⚠️> |

### Sentiment — <score>
> "<verbatim quote 1>"
> "<verbatim quote 2>"
> "<verbatim quote 3>"

### Pain level — <score>
> "<verbatim quote 1>"
> "<verbatim quote 2>"
> "<verbatim quote 3>"

### Excitement about solution — <score>
> "<verbatim quote 1>"
> "<verbatim quote 2>"
> "<verbatim quote 3>"
```

For low-confidence scores, add a single line under the quotes explaining why (e.g. "⚠️ Only 2 supporting quotes; respondent's tone is mixed between turns 4 and 7.").

For batch inputs, repeat the block per response, then optionally add:

```markdown
## Aggregate
- Sentiment: mean <x.x>, range <min–max>
- Pain: mean <x.x>, range <min–max>
- Excitement: mean <x.x>, range <min–max>

Themes: <1–3 bullet observations across the batch>
```

## Worked example

**Input:**
> "Honestly the current tool is killing us. We spend maybe two hours a day just exporting CSVs and reconciling them by hand — every single day. I've raised it three times this quarter. When you showed me the auto-sync demo I actually got a bit emotional, it's exactly what we need. If it does what you say, we'd switch tomorrow."

**Output:**

## Response analysis

| Dimension | Score | Confidence |
|---|---|---|
| Sentiment | 4 | high |
| Pain level | 5 | high |
| Excitement about solution | 5 | high |

### Sentiment — 4
> "Honestly the current tool is killing us."
> "When you showed me the auto-sync demo I actually got a bit emotional"
> "it's exactly what we need"

Sentiment lands at 4 rather than 5 because the strongly positive feeling is directed at the proposed solution; tone toward the existing tool is sharply negative, making the overall response mixed-but-leaning-positive.

### Pain level — 5
> "the current tool is killing us"
> "We spend maybe two hours a day just exporting CSVs and reconciling them by hand — every single day"
> "I've raised it three times this quarter"

### Excitement about solution — 5
> "I actually got a bit emotional"
> "it's exactly what we need"
> "we'd switch tomorrow"

## Guardrails

- **Never paraphrase quotes.** If a quote would need to be tidied to fit, leave it untidied. Verbatim is the whole point of the evidence rule.
- **Don't invent quotes.** If the source doesn't contain a supporting quote, flag it as low-confidence rather than fabricating one.
- **Don't pad with weak quotes.** A quote only counts as supporting evidence if, read alone, it would point a reasonable reader toward the score. A bare noun phrase or topic mention (e.g. "the integration you're describing") doesn't qualify — it shows what's being discussed, not how the respondent feels. Prefer 2 strong quotes plus a low-confidence flag over 3 quotes where one is filler.
- **Score the respondent, not the topic.** If someone calmly describes a catastrophic problem, sentiment may still be neutral (3) even though pain is 5.
- **Sentiment and excitement are different.** Sentiment is the overall emotional tone; excitement is specifically the reaction to a proposed solution. They often diverge — a frustrated customer (low sentiment) can be excited about a fix (high excitement).
- **Don't add dimensions the user didn't ask for.** Stick to the three. If the user wants more (e.g. urgency, willingness to pay), ask before adding.
