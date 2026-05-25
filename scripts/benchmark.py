from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aidetect import analyze_text


@dataclass(frozen=True)
class Case:
    name: str
    label: str
    text: str


AI_SENTENCES = [
    "In conclusion, it is important to note that this comprehensive approach provides a nuanced perspective for modern teams.",
    "First, the framework unlocks not only operational efficiency but also a sustainable path toward long-term success.",
    "Moreover, this outcome is a testament to the value of thoughtful planning, clear communication, and continuous improvement.",
    "Ultimately, the solution offers a robust, scalable, and comprehensive foundation for future growth.",
]

HUMAN_SENTENCES = [
    "I rewrote the opening after lunch because the first version sounded like a memo nobody would finish.",
    "The useful detail was not the big claim, but the small note about which door stuck whenever it rained.",
    "Our team kept the boring fix because it was the one we could explain, test, and support next month.",
    "Mina disagreed with the estimate, so we walked through the spreadsheet and found two assumptions that were simply old.",
    "No one loved the compromise, although Sam admitted it made the rollout less fragile.",
    "I still have a photo of the whiteboard because the arrows were easier to understand than my notes.",
    "The customer quote stayed in the draft because it named the exact pain: invoices vanished after export.",
    "On Tuesday we removed the clever queue idea and replaced it with a plain retry button.",
    "That choice made the demo less impressive, but support could explain it in one sentence.",
    "Priya caught the timezone bug by reading the logs backward from the failed receipt.",
    "The final paragraph is shorter now because the long version tried too hard to sound certain.",
    "I would rather ship the honest limitation than bury it under confident language.",
    "By the end, the plan had two owners, one date, and a test that had already failed once.",
    "The strange part is that the smallest change made the whole process feel calmer.",
    "We left one question open in the document so finance could answer it with real numbers.",
    "That is less tidy than a polished summary, but it matches what actually happened.",
]

MIXED_SENTENCES = [
    "The report gives a structured overview of the decision, but it also includes several specific notes from the meeting.",
    "However, the final recommendation should be reviewed against the original notes and the team's known writing style.",
    "A few passages are polished and repetitive, while others include concrete revisions, dates, and unresolved tradeoffs.",
]


def _repeat(sentences: list[str], count: int) -> str:
    return " ".join(sentences[i % len(sentences)] for i in range(count))


def build_cases() -> list[Case]:
    return [
        Case("ai_like_160", "ai_like", _repeat(AI_SENTENCES, 16)),
        Case("ai_like_320", "ai_like", _repeat(AI_SENTENCES, 32)),
        Case("human_like_160", "human_like", _repeat(HUMAN_SENTENCES, 16)),
        Case("human_like_320", "human_like", _repeat(HUMAN_SENTENCES, 32)),
        Case("mixed_180", "mixed", _repeat(MIXED_SENTENCES, 18)),
        Case("short_20", "short", "This short sample is intentionally too brief for a responsible detector decision."),
    ]


def run_cases(cases: list[Case]) -> list[dict]:
    rows = []
    for case in cases:
        result = analyze_text(case.text)
        rows.append({
            "case": case.name,
            "label": case.label,
            "words": result.word_count,
            "score": result.score,
            "confidence": result.confidence,
            "verdict": result.verdict,
        })
    return rows


def _mean_score(rows: list[dict], label: str) -> float:
    scores = [row["score"] for row in rows if row["label"] == label]
    return statistics.mean(scores) if scores else 0.0


def render_markdown(rows: list[dict]) -> str:
    ai_mean = _mean_score(rows, "ai_like")
    human_mean = _mean_score(rows, "human_like")
    separation = ai_mean - human_mean
    lines = [
        "# Benchmark Report",
        "",
        "This benchmark uses a tiny synthetic corpus to sanity-check score ordering, output stability, and short-text handling.",
        "It is not a claim of real-world detector accuracy.",
        "",
        "## Summary",
        "",
        f"- AI-like mean score: {ai_mean:.1f}",
        f"- Human-like mean score: {human_mean:.1f}",
        f"- Synthetic separation: {separation:.1f} points",
        "- Short samples should return `insufficient_text`.",
        "",
        "## Cases",
        "",
        "| Case | Label | Words | Score | Confidence | Verdict |",
        "| --- | --- | ---: | ---: | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['case']} | {row['label']} | {row['words']} | {row['score']} | {row['confidence']} | {row['verdict']} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "The intended pass condition is directional: AI-like synthetic text should score higher than human-like synthetic text, mixed text should remain uncertain, and very short text should not receive a normal authorship-risk verdict.",
        "",
        "For real deployments, add domain-specific examples and false-positive cases before making workflow decisions.",
    ])
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the ai-detector synthetic benchmark.")
    parser.add_argument("--markdown", type=Path, help="Write a Markdown report to this path.")
    args = parser.parse_args(argv)

    rows = run_cases(build_cases())
    report = render_markdown(rows)
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(report, encoding="utf-8")
    else:
        print(report)

    ai_mean = _mean_score(rows, "ai_like")
    human_mean = _mean_score(rows, "human_like")
    short_ok = any(row["label"] == "short" and row["verdict"] == "insufficient_text" for row in rows)
    return 0 if ai_mean > human_mean and short_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
