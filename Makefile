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
	python -m bench.runner pg_rel

bench-all:
	python -m bench.runner pg_rel
	python -m bench.runner pg_jsonb
	python -m bench.runner memgraph
	python -m bench.runner oxigraph

bench-pg:
	python -m bench.runner pg_rel
	python -m bench.runner pg_jsonb

bench-mg:
	python -m bench.runner memgraph

bench-ox:
	python -m bench.runner oxigraph

bench-clean:
	rm -f bench/results/*.json bench/results/*.csv

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

mg-up:
	docker compose up -d memgraph

mg-load:
	python loaders/memgraph/load.py --uri bolt://localhost:7688 --nodes-file dataset_gen/out/nodes.json --edges-file dataset_gen/out/edges.json

mg-q1:
	@echo "Exemple: docker compose exec -T memgraph mgconsole --file queries/cypher/Q1_energy_chain.cypher"

mg-q2:
	@echo "Exemple: docker compose exec -T memgraph mgconsole --file queries/cypher/Q2_functional_impact.cypher"

mg-q3:
	@echo "Exemple: docker compose exec -T memgraph mgconsole --file queries/cypher/Q3_space_services.cypher"

mg-q4:
	@echo "Exemple: docker compose exec -T memgraph mgconsole --file queries/cypher/Q4_inventory_floor_temp_points.cypher"

mg-q5:
	@echo "Exemple: docker compose exec -T memgraph mgconsole --file queries/cypher/Q5_orphans.cypher"

mg-q6:
	@echo "Not applicable dans Memgraph: utiliser TimescaleDB pour l'agrégation horaire"

mg-q7:
	@echo "Not applicable dans Memgraph: utiliser TimescaleDB pour la détection de dérive"

mg-q8:
	@echo "Exemple: docker compose exec -T memgraph mgconsole --file queries/cypher/Q8_tenant_served_energy.cypher"
