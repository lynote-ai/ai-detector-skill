import json

from aidetect.cli import main


def test_cli_json_reads_stdin(monkeypatch, capsys):
    text = " ".join([
        "In conclusion, it is important to note that this comprehensive overview is intentionally long enough.",
        "First, it includes several explicit transitions and a polished structure for the analyzer to inspect.",
    ] * 10)
    monkeypatch.setattr("sys.stdin", type("Stdin", (), {"read": lambda self: text})())

    assert main(["--json"]) == 0

    data = json.loads(capsys.readouterr().out)
    assert data["word_count"] >= 80
    assert data["conclusion"]


def test_cli_human_report_includes_required_sections(tmp_path, capsys):
    sample = tmp_path / "sample.txt"
    sample.write_text(" ".join([
        "The draft started as a rough note after the workshop and kept some of that uneven shape.",
        "It mentions one concrete mistake, one delayed decision, and one practical next step.",
    ] * 10), encoding="utf-8")

    assert main([str(sample)]) == 0

    output = capsys.readouterr().out
    assert "Conclusion:" in output
    assert "Score:" in output
    assert "Confidence:" in output
    assert "Caveats:" in output
