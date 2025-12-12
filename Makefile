SHELL := /bin/bash

PG_PROFILE ?= rel
PG_DIR := loaders/postgres
PSQL ?= psql
PG_CONN ?=

ifeq (,$(filter $(PG_PROFILE),rel jsonb))
$(error PG_PROFILE doit valoir rel ou jsonb)
endif

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

pg-init:
	$(PSQL) $(PG_CONN) -v ON_ERROR_STOP=1 -f $(PG_DIR)/schema_$(PG_PROFILE).sql
	$(PSQL) $(PG_CONN) -v ON_ERROR_STOP=1 -f $(PG_DIR)/timeseries.sql
	$(PSQL) $(PG_CONN) -v ON_ERROR_STOP=1 -f $(PG_DIR)/indexes_$(PG_PROFILE).sql

pg-load:
	$(if $(NODES_CSV),,$(error Merci de définir NODES_CSV=/chemin/nodes.csv))
	$(if $(EDGES_CSV),,$(error Merci de définir EDGES_CSV=/chemin/edges.csv))
	$(PSQL) $(PG_CONN) -v ON_ERROR_STOP=1 -v nodes_csv=$(NODES_CSV) -f $(PG_DIR)/load_nodes_$(PG_PROFILE).sql
	$(PSQL) $(PG_CONN) -v ON_ERROR_STOP=1 -v edges_csv=$(EDGES_CSV) -f $(PG_DIR)/load_edges_$(PG_PROFILE).sql

pg-queries:
	$(PSQL) $(PG_CONN) -v ON_ERROR_STOP=1 -f $(PG_DIR)/queries_$(PG_PROFILE).sql
