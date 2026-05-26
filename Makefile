.PHONY: test demo benchmark eval-hc3

test:
	PYTHONPATH=src python -m pytest -q

demo:
	PYTHONPATH=src python -m aidetect.cli examples/sample_ai_like.txt

benchmark:
	PYTHONPATH=src python scripts/benchmark.py --markdown docs/BENCHMARK.md

eval-hc3:
	PYTHONPATH=src python scripts/evaluate_hc3.py --markdown docs/HC3_EVALUATION.md
