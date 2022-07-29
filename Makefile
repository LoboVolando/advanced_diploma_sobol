run:
	cd ./application/src
	gunicorn application.src.app:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
up:
	docker-compose up application
down:
	docker-compose dowm
isort:
	isort --check-only --profile black ./api
black:
	black --check --diff -v ./api
flake:
	flake8 ./api
mypy:
	mypy ./api -v
lint:
	isort --check-only --profile black ./api
	black --check --diff -v ./api
	flake8 ./api
