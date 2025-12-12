SHELL := /bin/bash

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

ps:
	docker compose ps

clean:
	@echo "Attention: suppression des volumes et données persistantes" && docker compose down -v

gen:
	@echo "Not implemented yet" && exit 1

load:
	@echo "Not implemented yet" && exit 1

bench:
	@echo "Not implemented yet" && exit 1
