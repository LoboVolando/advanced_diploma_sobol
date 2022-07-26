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
