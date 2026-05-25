from __future__ import annotations

from dataclasses import asdict, dataclass
import re
import statistics
import zlib

_AI_MARKERS = [
    r"\bas an ai\b", r"\bi cannot\b", r"\bit is important to note\b",
    r"\bdelve\b", r"\bnuanced\b", r"\btestament to\b", r"\bunlock\b",
    r"\bcomprehensive\b", r"\bin conclusion\b", r"\boverall\b",
    r"\bnot only .* but also\b", r"\bwhile .* it is also\b",
]

_TRANSITIONS = [
    "first", "second", "third", "moreover", "furthermore", "however", "therefore",
    "ultimately", "additionally", "in summary", "in conclusion", "on the other hand",
]

@dataclass(frozen=True)
class Signal:
    name: str
    value: float
    weight: float
    note: str

@dataclass(frozen=True)
class DetectionResult:
    score: int
    verdict: str
    confidence: str
    word_count: int
    conclusion: str
    signals: list[Signal]
    caveats: list[str]
    next_steps: list[str]

    def to_dict(self) -> dict:
        data = asdict(self)
        data["signals"] = [asdict(s) for s in self.signals]
        return data

    def strongest_signals(self, limit: int = 4) -> list[Signal]:
        return sorted(
            self.signals,
            key=lambda s: (s.value * s.weight, s.weight),
            reverse=True,
        )[:limit]


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?。！？])\s+|[\n]+", text) if s.strip()]


def _words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z'\-]*|[\u4e00-\u9fff]", text.lower())


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _score_to_verdict(score: int) -> str:
    if score >= 70:
        return "high_ai_likelihood"
    if score >= 45:
        return "mixed_or_uncertain"
    return "low_ai_likelihood"


def _score_to_conclusion(verdict: str, score: int, confidence: str) -> str:
    if verdict == "insufficient_text":
        return "The sample is too short for a meaningful estimate, so any AI-like reading would be highly uncertain."
    if verdict == "high_ai_likelihood":
        return f"AI-like signals are present, but this {confidence}-confidence score is a risk estimate rather than proof."
    if verdict == "mixed_or_uncertain":
        return f"The sample shows mixed AI-like and human-like signals, so the result is uncertain at {score}/100."
    return f"AI-like signals are limited in this sample, though the result remains an imperfect estimate."


def analyze_text(text: str) -> DetectionResult:
    """Analyze text for AI-like writing signals.

    This is not a forensic detector. It returns a risk estimate with evidence so an
    agent can review, ask better questions, and avoid overclaiming.
    """
    raw = text or ""
    normalized = re.sub(r"\s+", " ", raw).strip()
    words = _words(normalized)
    sentences = _sentences(raw)
    word_count = len(words)

    if word_count < 80:
        verdict = "insufficient_text"
        return DetectionResult(
            score=0,
            verdict=verdict,
            confidence="low",
            word_count=word_count,
            conclusion=_score_to_conclusion(verdict, 0, "low"),
            signals=[],
            caveats=["Provide at least ~80 words for a less noisy estimate."],
            next_steps=["Ask for a longer sample before drawing any conclusion."],
        )

    sentence_lengths = [max(1, len(_words(s))) for s in sentences] or [word_count]
    avg_len = statistics.mean(sentence_lengths)
    stdev_len = statistics.pstdev(sentence_lengths) if len(sentence_lengths) > 1 else 0.0
    burstiness = stdev_len / avg_len if avg_len else 0.0

    unique_ratio = len(set(words)) / word_count
    marker_hits = sum(1 for p in _AI_MARKERS if re.search(p, normalized, re.I | re.S))
    transition_hits = sum(normalized.lower().count(t) for t in _TRANSITIONS)

    listish_lines = len(re.findall(r"(?m)^\s*(?:[-*•]|\d+[.)])\s+", raw))
    headingish_lines = len(re.findall(r"(?m)^\s{0,3}#{1,3}\s+|^\s{0,3}[A-Z][A-Za-z ]{3,}:\s*$", raw))

    compressed = len(zlib.compress(normalized.encode("utf-8")))
    compression_ratio = compressed / max(1, len(normalized.encode("utf-8")))

    signals: list[Signal] = []
    signals.append(Signal(
        "low_burstiness", _clamp01((0.62 - burstiness) / 0.62), 0.20,
        f"Sentence-length variation is {'low' if burstiness < 0.35 else 'normal'}; burstiness={burstiness:.2f}.",
    ))
    signals.append(Signal(
        "formulaic_markers", _clamp01(marker_hits / 5), 0.22,
        f"Matched {marker_hits} common AI-like phrase patterns.",
    ))
    signals.append(Signal(
        "transition_density", _clamp01((transition_hits / max(1, word_count)) * 55), 0.14,
        f"Found {transition_hits} explicit discourse transitions across {word_count} words.",
    ))
    signals.append(Signal(
        "lexical_smoothness", _clamp01((0.62 - unique_ratio) / 0.32), 0.18,
        f"Unique-token ratio={unique_ratio:.2f}; lower values can indicate templated prose.",
    ))
    signals.append(Signal(
        "structured_answer_shape", _clamp01((listish_lines + headingish_lines) / 8), 0.12,
        f"Detected {listish_lines} list-like lines and {headingish_lines} heading-like lines.",
    ))
    signals.append(Signal(
        "compressibility", _clamp01((0.55 - compression_ratio) / 0.28), 0.14,
        f"Compression ratio={compression_ratio:.2f}; highly compressible text may be repetitive.",
    ))

    score = round(sum(s.value * s.weight for s in signals) / sum(s.weight for s in signals) * 100)
    verdict = _score_to_verdict(score)
    confidence = "medium" if word_count >= 250 else "low"

    caveats = [
        "Do not use this as proof of authorship or misconduct.",
        "Paraphrasing, editing, domain style, ESL writing, templates, and short samples can distort results.",
        "For high-stakes use, compare against known writing samples and require human review.",
    ]
    next_steps = [
        "Review the strongest signals in context instead of treating the score as a verdict.",
    ]
    if confidence == "low":
        next_steps.append("Use a longer sample, ideally 250+ words, before relying on the estimate.")
    if score >= 45:
        next_steps.append("Compare with known writing samples if the context has consequences for a person.")

    return DetectionResult(
        score=score,
        verdict=verdict,
        confidence=confidence,
        word_count=word_count,
        conclusion=_score_to_conclusion(verdict, score, confidence),
        signals=signals,
        caveats=caveats,
        next_steps=next_steps,
    )
