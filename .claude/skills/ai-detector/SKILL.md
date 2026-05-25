---
name: ai-detector
description: Evidence-based AI-generated text risk analysis for essays, emails, reviews, articles, messages, and other prose samples.
---

# AI Detector

Use this skill when a user asks whether a passage may be AI-generated.

## Core Rules

- Never present the score as proof.
- Never accuse a named person of cheating, fraud, or misconduct.
- Ask for a longer sample when the text is under about 80 words.
- Prefer "AI-like signals are present" over "This was written by AI".
- For high-stakes contexts, recommend human review and comparison with known writing samples.

## Run

From this repository:

```bash
ai-detect path/to/text.txt --json
```

or:

```bash
python -m aidetect.cli path/to/text.txt --json
```

## Respond

1. Give a one-sentence conclusion with uncertainty.
2. Show score and confidence.
3. List the strongest evidence signals.
4. Include caveats.
5. Suggest next steps only when useful.

## Wording

Good:

- "AI-like signals are present, but this is not proof."
- "The result is uncertain because the sample is short."
- "This should be reviewed by a human and compared with known writing samples."

Avoid:

- "This was definitely written by AI."
- "The detector proves misconduct."
- Any accusation against a named person.
