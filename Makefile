run:
	cd ./backend/src
	gunicorn src.app:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
up:
	docker-compose up backend
down:
	docker-compose dowm
isort:
	isort --check-only --profile black ./backend
black:
	black --check --diff -v ./backend
flake:
	flake8 ./api
mypy:
	mypy ./api -v
lint:
	isort --check-only --profile black ./backend
	black --check --diff -v ./backend
	flake8 ./backend

flint:
	isort --profile black ./backend
	black ./backend
