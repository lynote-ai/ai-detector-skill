from __future__ import annotations

import argparse
import json
import sys
from .core import analyze_text


def _print_human_report(result) -> None:
    print(f"Conclusion: {result.conclusion}")
    print(f"Score: {result.score}/100")
    print(f"Confidence: {result.confidence}")
    print(f"Verdict: {result.verdict}")
    print(f"Words analyzed: {result.word_count}")

    if result.signals:
        print("\nStrongest evidence signals:")
        for signal in result.strongest_signals():
            print(f"- {signal.name}: {signal.value:.2f} x {signal.weight:.2f} - {signal.note}")

    print("\nCaveats:")
    for caveat in result.caveats:
        print(f"- {caveat}")

    if result.next_steps:
        print("\nSuggested next steps:")
        for step in result.next_steps:
            print(f"- {step}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evidence-based AI-like text risk analyzer.")
    parser.add_argument("path", nargs="?", help="Text file to analyze. Reads stdin when omitted.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args(argv)

    if args.path:
        with open(args.path, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    result = analyze_text(text)
    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0

    _print_human_report(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
