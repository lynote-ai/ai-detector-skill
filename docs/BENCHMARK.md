# Benchmark Report

This benchmark uses a tiny synthetic corpus to sanity-check score ordering, output stability, and short-text handling.
It is not a claim of real-world detector accuracy.

## Summary

- AI-like mean score: 84.0
- Human-like mean score: 35.0
- Synthetic separation: 49.0 points
- Short samples should return `insufficient_text`.

## Cases

| Case | Label | Words | Score | Confidence | Verdict |
| --- | --- | ---: | ---: | --- | --- |
| ai_like_160 | ai_like | 256 | 84 | medium | high_ai_likelihood |
| ai_like_320 | ai_like | 512 | 84 | medium | high_ai_likelihood |
| human_like_160 | human_like | 259 | 20 | medium | low_ai_likelihood |
| human_like_320 | human_like | 518 | 50 | medium | mixed_or_uncertain |
| mixed_180 | mixed | 312 | 64 | medium | mixed_or_uncertain |
| short_20 | short | 12 | 0 | low | insufficient_text |

## Interpretation

The intended pass condition is directional: AI-like synthetic text should score higher than human-like synthetic text, mixed text should remain uncertain, and very short text should not receive a normal authorship-risk verdict.

For real deployments, add domain-specific examples and false-positive cases before making workflow decisions.
