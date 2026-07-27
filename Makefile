.PHONY: install install-semantic test doctor smoke suite manual-deepseek manual-gemini deepseek-api gemini-api pilot-plan pilot-check pilot pilot-blind battery-plan battery-check battery battery-blind clean

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

manual-deepseek:
	embodied-llm doctor --config configs/manual/deepseek-web.yaml
	embodied-llm run --config configs/manual/deepseek-web.yaml

manual-gemini:
	embodied-llm doctor --config configs/manual/gemini-web.yaml
	embodied-llm run --config configs/manual/gemini-web.yaml

deepseek-api:
	embodied-llm doctor --config configs/providers/deepseek-api.yaml
	embodied-llm run --config configs/providers/deepseek-api.yaml

gemini-api:
	embodied-llm doctor --config configs/providers/gemini-api.yaml
	embodied-llm run --config configs/providers/gemini-api.yaml

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
	rm -rf runs suite-runs manual-runs manual-sessions provider-runs .pytest_cache .ruff_cache build dist *.egg-info src/*.egg-info