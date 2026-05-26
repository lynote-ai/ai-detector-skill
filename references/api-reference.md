# API Reference

## CLI

Primary command:

```bash
ai-detect path/to/text.txt --json
```

Alternative entry points:

```bash
python -m aidetect.cli path/to/text.txt --json
python scripts/detect.py path/to/text.txt --json
```

When no file path is provided, the CLI reads from stdin.

## JSON Output Contract

The detector returns a JSON object with these public fields:

- `score`: integer from 0 to 100
- `verdict`: one of `insufficient_text`, `low_ai_likelihood`, `mixed_or_uncertain`, `high_ai_likelihood`
- `confidence`: currently `low` or `medium`
- `word_count`: analyzed word count
- `conclusion`: cautious one-sentence summary
- `signals`: weighted evidence signal objects
- `caveats`: list of caution statements
- `next_steps`: suggested follow-up actions

Each `signals` item includes:

- `name`
- `value`
- `weight`
- `note`

## Interpretation Rules

- Treat the score as a risk estimate, not proof.
- Very short samples should return `insufficient_text`.
- High-stakes decisions should involve human review and comparison with known writing samples.
