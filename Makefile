PYTHON ?= python

.PHONY: demo demos test clean

demo:
	$(PYTHON) main.py --config data/demo.yaml

demos:
	$(PYTHON) run_all_demos.py

test:
	pytest

clean:
	rm -rf outputs/demo_run outputs/large_trade_shock outputs/il_stress outputs/demo outputs/demo_large_trade_shock outputs/demo_il_stress outputs/demo_comparison.json
