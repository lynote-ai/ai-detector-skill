from aidetect import analyze_text


def test_short_text_is_insufficient():
    result = analyze_text("Too short.")
    assert result.verdict == "insufficient_text"
    assert result.confidence == "low"
    assert result.word_count < 80
    assert result.next_steps
    assert "too short" in result.conclusion.lower()


def test_long_text_returns_evidence():
    text = " ".join([
        "In conclusion, it is important to note that this comprehensive overview provides a nuanced perspective.",
        "First, the system considers multiple signals. Moreover, it avoids making absolute claims.",
        "However, the result should be treated as a risk estimate rather than proof.",
    ] * 8)
    result = analyze_text(text)
    assert 0 <= result.score <= 100
    assert result.signals
    assert result.verdict in {"low_ai_likelihood", "mixed_or_uncertain", "high_ai_likelihood"}
    assert result.strongest_signals()


def test_ai_like_sample_scores_higher_than_human_like_sample():
    ai_like = " ".join([
        "In conclusion, it is important to note that this comprehensive overview provides a nuanced perspective.",
        "First, the framework unlocks not only meaningful productivity but also sustainable long-term value.",
        "Moreover, the solution is a testament to the importance of careful planning and structured execution.",
        "Ultimately, this approach offers a robust and comprehensive path forward for modern teams.",
    ] * 16)
    human_like = " ".join([
        "I left the meeting with three messy notes and a coffee ring on the page.",
        "The first idea sounded clever in the room, but it fell apart when Mara asked who would maintain it.",
        "We argued for ten minutes, crossed out two assumptions, and kept the one boring fix that would actually ship.",
        "By Friday the patch was small, readable, and a little less glamorous than the pitch.",
    ] * 16)

    assert analyze_text(ai_like).score > analyze_text(human_like).score


def test_result_dict_contains_public_contract_fields():
    text = " ".join([
        "This paragraph has enough words to exercise the public result contract.",
        "It should include the score, confidence, conclusion, caveats, next steps, and weighted evidence signals.",
    ] * 10)

    data = analyze_text(text).to_dict()

    assert {"score", "verdict", "confidence", "word_count", "conclusion", "signals", "caveats", "next_steps"} <= set(data)
