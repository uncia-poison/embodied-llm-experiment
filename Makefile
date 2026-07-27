.PHONY: install install-semantic test doctor smoke suite pilot battery clean

install:
	python -m pip install -e .[dev]

install-semantic:
	python -m pip install -e .[dev,semantic]

test:
	pytest

doctor:
	embodied-llm doctor --config configs/mvp.yaml

smoke:
	embodied-llm run --config configs/mvp.yaml

suite:
	embodied-llm suite --suite configs/suites/mock-battery.yaml

pilot:
	embodied-llm doctor --config configs/suites/u3-semantic.yaml
	embodied-llm suite --suite configs/suites/causal-subject-pilot.yaml

battery:
	embodied-llm doctor --config configs/suites/u3-semantic.yaml
	embodied-llm suite --suite configs/suites/causal-subject-battery.yaml

clean:
	rm -rf runs suite-runs .pytest_cache .ruff_cache build dist *.egg-info src/*.egg-info
