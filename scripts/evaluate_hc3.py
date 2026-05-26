from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
from statistics import mean
import sys
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aidetect import analyze_text


DATASET_NAME = "Hello-SimpleAI/HC3"
DEFAULT_SUBSETS = ("finance", "medicine", "open_qa")


def _download_lines(subset: str) -> list[str]:
    url = f"https://huggingface.co/datasets/{DATASET_NAME}/resolve/main/{subset}.jsonl?download=true"
    with urlopen(url) as response:
        payload = response.read().decode("utf-8")
    return payload.splitlines()


def _collect_examples(subsets: tuple[str, ...], limit: int) -> list[dict]:
    rows: list[dict] = []
    for subset in subsets:
        for line in _download_lines(subset)[:limit]:
            item = json.loads(line)
            human = (item.get("human_answers") or [""])[0].strip()
            ai = (item.get("chatgpt_answers") or [""])[0].strip()
            if human:
                rows.append({"subset": subset, "label": "human", "text": human})
            if ai:
                rows.append({"subset": subset, "label": "ai", "text": ai})
    return rows


def _evaluate(rows: list[dict]) -> list[dict]:
    results: list[dict] = []
    for row in rows:
        result = analyze_text(row["text"])
        results.append({
            "subset": row["subset"],
            "label": row["label"],
            "score": result.score,
            "verdict": result.verdict,
            "confidence": result.confidence,
            "word_count": result.word_count,
        })
    return results


def _summarize(results: list[dict]) -> dict:
    summary: dict = {"overall": {}, "by_subset": {}}
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in results:
        grouped[row["subset"]].append(row)

    summary["overall"] = _summarize_bucket(results)
    for subset, rows in sorted(grouped.items()):
        summary["by_subset"][subset] = _summarize_bucket(rows)
    return summary


def _summarize_bucket(rows: list[dict]) -> dict:
    labels = {}
    for label in ("human", "ai"):
        xs = [row for row in rows if row["label"] == label]
        covered = [row for row in xs if row["verdict"] != "insufficient_text"]
        labels[label] = {
            "count": len(xs),
            "coverage": round(len(covered) / len(xs), 3) if xs else 0.0,
            "mean_score": round(mean(row["score"] for row in xs), 1) if xs else 0.0,
            "mean_score_covered": round(mean(row["score"] for row in covered), 1) if covered else 0.0,
            "mean_words": round(mean(row["word_count"] for row in xs), 1) if xs else 0.0,
            "verdicts": dict(Counter(row["verdict"] for row in xs)),
        }

    covered_all = [row for row in rows if row["verdict"] != "insufficient_text"]
    threshold_metrics = {}
    for threshold in (45, 70):
        if covered_all:
            correct = 0
            for row in covered_all:
                predicted = "ai" if row["score"] >= threshold else "human"
                correct += predicted == row["label"]
            threshold_metrics[str(threshold)] = {
                "covered_accuracy": round(correct / len(covered_all), 3),
                "sample_count": len(covered_all),
            }
        else:
            threshold_metrics[str(threshold)] = {"covered_accuracy": 0.0, "sample_count": 0}

    ai_mean = labels["ai"]["mean_score"]
    human_mean = labels["human"]["mean_score"]
    return {
        "labels": labels,
        "mean_separation": round(ai_mean - human_mean, 1),
        "threshold_metrics": threshold_metrics,
    }


def _render_markdown(summary: dict, subsets: tuple[str, ...], limit: int) -> str:
    overall = summary["overall"]
    lines = [
        "# HC3 Evaluation Report",
        "",
        "This report evaluates the current heuristic detector against a reproducible slice of the public HC3 English dataset.",
        "",
        "## Dataset",
        "",
        f"- Source: `Hello-SimpleAI/HC3`",
        f"- Subsets: `{', '.join(subsets)}`",
        f"- Rows per subset: first `{limit}` question-answer pairs",
        "- Labels used: first `human_answers[0]` vs first `chatgpt_answers[0]`",
        "- Evaluation date: `2026-05-26`",
        "",
        "## Overall Results",
        "",
        f"- Human mean score: `{overall['labels']['human']['mean_score']}`",
        f"- AI mean score: `{overall['labels']['ai']['mean_score']}`",
        f"- Mean separation: `{overall['mean_separation']}` points",
        f"- Human coverage (not `insufficient_text`): `{overall['labels']['human']['coverage']}`",
        f"- AI coverage (not `insufficient_text`): `{overall['labels']['ai']['coverage']}`",
        f"- Covered accuracy at `score >= 45`: `{overall['threshold_metrics']['45']['covered_accuracy']}` over `{overall['threshold_metrics']['45']['sample_count']}` texts",
        f"- Covered accuracy at `score >= 70`: `{overall['threshold_metrics']['70']['covered_accuracy']}` over `{overall['threshold_metrics']['70']['sample_count']}` texts",
        "",
        "## Verdict Distribution",
        "",
        f"- Human: `{overall['labels']['human']['verdicts']}`",
        f"- AI: `{overall['labels']['ai']['verdicts']}`",
        "",
        "## Per-Subset Summary",
        "",
        "| Subset | Human Mean | AI Mean | Separation | Human Coverage | AI Coverage |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for subset, bucket in summary["by_subset"].items():
        lines.append(
            f"| {subset} | {bucket['labels']['human']['mean_score']} | {bucket['labels']['ai']['mean_score']} | "
            f"{bucket['mean_separation']} | {bucket['labels']['human']['coverage']} | {bucket['labels']['ai']['coverage']} |"
        )

    lines.extend([
        "",
        "## Interpretation",
        "",
        "1. The detector separates human and AI answers in average score, but only weakly on this HC3 slice.",
        "2. The short-text guardrail is active, especially for HC3 human answers, so a large share of human texts become `insufficient_text` rather than forced classifications.",
        "3. With the current score bands, the detector rarely escalates to `mixed_or_uncertain` or `high_ai_likelihood` on HC3. That keeps it cautious, but also means recall is low for this dataset.",
        "4. This result supports positioning the project as a triage and explanation tool, not a stand-alone classifier.",
        "",
        "## Reproduce",
        "",
        "```bash",
        "python scripts/evaluate_hc3.py --markdown docs/HC3_EVALUATION.md",
        "```",
        "",
        "## Caveats",
        "",
        "- HC3 is a QA-style corpus, not a general-purpose essay benchmark.",
        "- This report uses only the first answer from each side and only the first rows from each subset.",
        "- The current detector is intentionally heuristic and conservative; these numbers should not be described as forensic accuracy.",
    ])
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate the AI detector on a slice of the HC3 dataset.")
    parser.add_argument("--limit", type=int, default=100, help="Rows per subset to evaluate.")
    parser.add_argument(
        "--subsets",
        nargs="+",
        default=list(DEFAULT_SUBSETS),
        help="HC3 English subsets to evaluate.",
    )
    parser.add_argument("--markdown", type=Path, help="Write a Markdown report to this path.")
    args = parser.parse_args(argv)

    subsets = tuple(args.subsets)
    results = _evaluate(_collect_examples(subsets, args.limit))
    summary = _summarize(results)
    report = _render_markdown(summary, subsets, args.limit)

    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(report, encoding="utf-8")
    else:
        print(report)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
