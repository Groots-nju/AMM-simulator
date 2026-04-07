PYTHON ?= python

.PHONY: demo demos test web-backend web-frontend clean

demo:
	$(PYTHON) main.py --config data/demo.yaml

demos:
	$(PYTHON) run_all_demos.py

test:
	pytest

web-backend:
	$(PYTHON) -m uvicorn backend.app.main:app --reload --port 8000

web-frontend:
	cd frontend && npm run dev

clean:
	rm -rf outputs/demo_run outputs/large_trade_shock outputs/il_stress outputs/demo outputs/demo_large_trade_shock outputs/demo_il_stress outputs/demo_comparison.json
