# Agent Instructions: AI Detector Skill

Use this repository as an AI-generated text risk analysis tool.

## When to use

Use it when the user asks whether a passage, essay, email, article, review, or message may be AI-generated.

## Required behavior

- Never present the score as proof.
- Never accuse a named person of cheating, fraud, or misconduct.
- Ask for a longer sample when text is under ~80 words.
- Prefer: "AI-like signals are present" over "This was written by AI".
- For high-stakes contexts, recommend human review and comparison with known writing samples.

## How to run

```bash
ai-detect path/to/text.txt --json
```

or:

```bash
python -m aidetect.cli path/to/text.txt --json
```

## Response format for users

1. Give a one-sentence conclusion with uncertainty.
2. Show score and confidence.
3. List the strongest evidence signals.
4. Include caveats.
5. Suggest next steps only when useful.
