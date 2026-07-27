.PHONY: install install-semantic test doctor smoke suite pilot-plan pilot-check pilot pilot-blind battery-plan battery-check battery battery-blind clean

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

pilot-plan:
	embodied-llm suite --suite configs/suites/causal-subject-pilot.yaml --plan

pilot-check:
	embodied-llm suite --suite configs/suites/causal-subject-pilot.yaml --preflight

pilot:
	embodied-llm suite --suite configs/suites/causal-subject-pilot.yaml --preflight
	embodied-llm suite --suite configs/suites/causal-subject-pilot.yaml

pilot-blind:
	embodied-llm blind suite-runs/causal-subject-pilot-v1

battery-plan:
	embodied-llm suite --suite configs/suites/causal-subject-battery.yaml --plan

battery-check:
	embodied-llm suite --suite configs/suites/causal-subject-battery.yaml --preflight

battery:
	embodied-llm suite --suite configs/suites/causal-subject-battery.yaml --preflight
	embodied-llm suite --suite configs/suites/causal-subject-battery.yaml

battery-blind:
	embodied-llm blind suite-runs/causal-subject-battery-v1

clean:
	rm -rf runs suite-runs .pytest_cache .ruff_cache build dist *.egg-info src/*.egg-info
