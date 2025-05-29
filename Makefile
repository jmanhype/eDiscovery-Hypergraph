up:
	docker compose up --build

down:
	docker compose down

test-elixir:
	cd apps/a2a_agent_web && mix test

test-python:
	cd agents/python_agents/minimal_a2a_agent && pytest

test:
	make test-elixir && make test-python

lint:
	cd apps/a2a_agent_web && mix format --check-formatted && ruff check ../../agents/python_agents/minimal_a2a_agent
