.PHONY: test demo benchmark

test:
	PYTHONPATH=src python -m pytest -q

demo:
	PYTHONPATH=src python -m aidetect.cli examples/sample_ai_like.txt

benchmark:
	PYTHONPATH=src python scripts/benchmark.py --markdown docs/BENCHMARK.md
