.PHONY: backend-install backend-run backend-test frontend-install frontend-dev docker-up docker-down

backend-install:
	python3 -m venv .venv && . .venv/bin/activate && pip install -r backend/requirements.txt

backend-run:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

backend-test:
	cd backend && pytest

frontend-install:
	cd frontend && npm install

frontend-dev:
	cd frontend && npm run dev

docker-up:
	docker compose up --build

docker-down:
	docker compose down
