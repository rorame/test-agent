.PHONY: install run serve docker-build docker-run clean

install:
	uv sync

run:
	uv run python main.py

serve:
	uv run python a2a_server.py

docker-build:
	docker build -t crossing-time-agent .

docker-run:
	docker run --rm --env-file .env -p 9000:9000 crossing-time-agent

clean:
	rm -rf .venv **/__pycache__ __pycache__
