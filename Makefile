.PHONY: install test smoke suite clean

install:
	python -m pip install -e .[dev]

test:
	pytest

smoke:
	embodied-llm run --config configs/mvp.yaml

suite:
	embodied-llm suite --suite configs/suites/mock-battery.yaml

clean:
	rm -rf runs suite-runs .pytest_cache .ruff_cache *.egg-info src/*.egg-info
