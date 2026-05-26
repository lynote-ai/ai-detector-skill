# HC3 Evaluation Report

This report evaluates the current heuristic detector against a reproducible slice of the public HC3 English dataset.

## Dataset

- Source: `Hello-SimpleAI/HC3`
- Subsets: `finance, medicine, open_qa`
- Rows per subset: first `100` question-answer pairs
- Labels used: first `human_answers[0]` vs first `chatgpt_answers[0]`
- Evaluation date: `2026-05-26`

## Overall Results

- Human mean score: `5.4`
- AI mean score: `18.4`
- Mean separation: `13.0` points
- Human coverage (not `insufficient_text`): `0.427`
- AI coverage (not `insufficient_text`): `0.92`
- Covered accuracy at `score >= 45`: `0.317` over `404` texts
- Covered accuracy at `score >= 70`: `0.317` over `404` texts

## Verdict Distribution

- Human: `{'insufficient_text': 172, 'low_ai_likelihood': 128}`
- AI: `{'low_ai_likelihood': 276, 'insufficient_text': 24}`

## Per-Subset Summary

| Subset | Human Mean | AI Mean | Separation | Human Coverage | AI Coverage |
| --- | ---: | ---: | ---: | ---: | ---: |
| finance | 8.4 | 22.2 | 13.8 | 0.7 | 0.98 |
| medicine | 2.8 | 19.2 | 16.4 | 0.37 | 0.91 |
| open_qa | 5.0 | 13.8 | 8.8 | 0.21 | 0.87 |

## Interpretation

1. The detector separates human and AI answers in average score, but only weakly on this HC3 slice.
2. The short-text guardrail is active, especially for HC3 human answers, so a large share of human texts become `insufficient_text` rather than forced classifications.
3. With the current score bands, the detector rarely escalates to `mixed_or_uncertain` or `high_ai_likelihood` on HC3. That keeps it cautious, but also means recall is low for this dataset.
4. This result supports positioning the project as a triage and explanation tool, not a stand-alone classifier.

## Reproduce

```bash
python scripts/evaluate_hc3.py --markdown docs/HC3_EVALUATION.md
```

## Caveats

- HC3 is a QA-style corpus, not a general-purpose essay benchmark.
- This report uses only the first answer from each side and only the first rows from each subset.
- The current detector is intentionally heuristic and conservative; these numbers should not be described as forensic accuracy.
