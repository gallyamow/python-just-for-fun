.PHONY: lint test

test:
	go test  ./...

lint:
	ruff check . --fix
	ruff format .

