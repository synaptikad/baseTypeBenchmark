# Runbook OVH B3 (BaseTypeBenchmark)

Date: 2025-12-21

## Objectif

Avoir une checklist **fiable et reproductible** pour exécuter le benchmark sur une instance OVH B3, en validant :

- Docker OK (daemon + droits user)
- cgroup v2 OK
- reset `memory.peak` OK (sans exécuter tout en root)
- génération dataset OK (quand HuggingFace ne contient pas les exports)
- démarrage + connexion aux services (TimescaleDB/PostgreSQL, Memgraph, Oxigraph)

---

## Bootstrap initial (FAIRE UNE SEULE FOIS)

Après un `git pull` sur B3, exécuter cette séquence **avant** tout smoke test :

```bash
cd ~/baseTypeBenchmark

# 1. Créer docker/.env à partir du template
cp config/benchmark.env docker/.env

# 2. Vérifier le contenu
grep POSTGRES docker/.env
# Attendu: POSTGRES_USER=postgres, POSTGRES_PASSWORD=benchmark, POSTGRES_DB=benchmark

# 3. Détruire les volumes existants (évite les credentials persistés)
cd docker
docker compose down -v

# 4. Démarrer TimescaleDB avec limite RAM
MEMORY_LIMIT=8g docker compose up -d timescaledb

# 5. Attendre que le conteneur soit healthy (~20s)
sleep 20
docker ps | grep btb_timescaledb
# Attendu: (healthy)

# 6. Tester la connexion
PGPASSWORD=benchmark psql -h localhost -U postgres -d benchmark -c 'SELECT 1;'
# Attendu: affiche "1"
```

Si l'étape 6 échoue, voir la section "Blocage actuel: connexion PostgreSQL".

---

## État actuel (ce qu'on a déjà validé)

- cgroup v2 présent sur la machine.
- `memory.peak` est **resettable**.
  - Écriture directe dans `/sys/fs/cgroup/...` nécessite des droits root.
  - Le code a été adapté pour tenter un fallback non-interactif `sudo -n`.
- La génération du dataset `small-2d` (seed 42) **fonctionne** et exporte ~10GB sur disque.
- Le smoke P1 échoue encore à l’étape de connexion PostgreSQL avec une erreur **non transiente**.

## Pré-requis côté OS

### Docker accessible en user

Symptôme :

- `permission denied while trying to connect to the Docker daemon socket ... /var/run/docker.sock`

Fix :

```bash
sudo usermod -aG docker ubuntu
newgrp docker
```

Validation :

```bash
docker ps
```

### Python venv

```bash
cd ~/baseTypeBenchmark
source .venv/bin/activate
python3 --version
```

## Vérifier `memory.peak` (cgroup v2)

But: confirmer que la mesure “peak RAM pendant phase requêtes” est possible et resettable.

Précondition : au moins **1 conteneur lancé** (pour avoir un cgroup concret).

```bash
cd ~/baseTypeBenchmark/docker
MEMORY_LIMIT=8g docker compose up -d timescaledb
```

Puis diagnostic:

```bash
cd ~/baseTypeBenchmark
python3 scripts/diagnose_env.py --containers btb_timescaledb
```

Attendu :

- `cgroup v2: True`
- `btb_timescaledb: cgroup ok, memory.peak reset_ok=True`

Si `reset_ok=False` :

- vérifier que `sudo -n` est autorisé (pas de prompt) :

```bash
sudo -n true && echo OK || echo FAIL
```

## Dataset: HuggingFace vs génération locale

Actuellement, le repo HuggingFace `synaptikad/basetype-benchmark` ne contient pas les exports (seulement README), donc le smoke bascule sur génération locale.

Recommandation :

- pour itérer rapidement, garder la génération locale sur B3.
- plus tard, publier les exports dans un repo HF datasets dédié (ou release assets) si besoin.

## Blocage actuel: connexion PostgreSQL (P1/P2)

### Symptôme

Pendant `scripts/smoke_benchmark.py`:

- conteneur TimescaleDB démarre
- puis `Connecting to PostgreSQL...`
- puis erreur “non transiente” (auth/config), typiquement user/db/MDP incorrects ou DB inexistante.

### Cause probable (la plus fréquente)

Le conteneur TimescaleDB est configuré via **docker/.env** (référencé par `docker/docker-compose.yml` via `env_file: .env`).

Si ce fichier est absent / incomplet / pas pris en compte, le conteneur peut démarrer avec des valeurs par défaut (ex: user `postgres`) tandis que le loader Python essaie de se connecter avec un autre user.

### Check 1: vérifier le contenu de `docker/.env`

```bash
cd ~/baseTypeBenchmark
sed -n '1,120p' docker/.env | egrep 'POSTGRES_|MEMORY_LIMIT' || true
```

Attendu (valeurs typiques) :

- `POSTGRES_USER=postgres`
- `POSTGRES_PASSWORD=benchmark`
- `POSTGRES_DB=benchmark`

Si absent :

```bash
cd ~/baseTypeBenchmark
cp -f config/benchmark.env docker/.env
```

### Check 2: vérifier ce que le conteneur a réellement reçu

Démarrer TimescaleDB puis inspecter ses envs:

```bash
cd ~/baseTypeBenchmark/docker
MEMORY_LIMIT=8g docker compose up -d timescaledb

docker inspect -f '{{range .Config.Env}}{{println .}}{{end}}' btb_timescaledb | egrep 'POSTGRES_' || true
```

Si tu vois `POSTGRES_PASSWORD=` vide, ou pas de `POSTGRES_*`, alors `.env` n’est pas pris en compte.

### Check 3: état santé + logs

```bash
docker ps
```

Attendu: `Up ... (healthy)`.

Si pas healthy:

```bash
docker logs btb_timescaledb --tail 200
```

### Check 4: tester la connexion depuis l’hôte

Installer `psql` si besoin:

```bash
sudo apt-get update -y
sudo apt-get install -y postgresql-client
```

Tester (ajuste user/db/pass selon `docker/.env`):

```bash
export PGPASSWORD=benchmark
psql -h localhost -p 5432 -U postgres -d benchmark -c 'SELECT 1;'
```

- Si ça marche, le service est OK, et le problème est dans la config côté Python.
- Si ça ne marche pas, c’est un problème de conteneur/credentials/volume.

### Check 5: volumes (credentials “persistés”)

Si tu as déjà démarré TimescaleDB avec d’autres `POSTGRES_USER/PASSWORD/DB`, le volume peut conserver un cluster initialisé. Dans ce cas, changer les envs ne re-crée pas l’utilisateur.

Pour repartir à zéro (⚠️ destructif, ok sur un test):

```bash
cd ~/baseTypeBenchmark/docker
docker compose down -v
```

Puis relancer:

```bash
MEMORY_LIMIT=8g docker compose up -d timescaledb
```

## Recommandations d’architecture (prochaines étapes)

1. **Single source of truth config**
   - aujourd’hui: Compose lit `docker/.env`, Python n’exporte pas forcément les variables.
   - recommendation: charger `docker/.env` côté Python au lancement (ex: `python-dotenv`) ou centraliser dans une config YAML.

2. **Start containers = attendre health**
   - la fonction de start attend 5s puis espère que le loader retry.
   - recommendation: attendre explicitement `healthy` quand `healthcheck` existe, avec un timeout.

3. **Mesure `memory.peak`**
   - validée sur B3 avec fallback `sudo -n`.
   - recommendation: documenter explicitement l’exigence “passwordless sudo” (ou fallback max(memory.current)).

## Commandes "step-by-step" recommandées (résumé)

### Après git pull (première fois ou après reset)

```bash
cd ~/baseTypeBenchmark

# Bootstrap env + volumes
cp config/benchmark.env docker/.env
cd docker && docker compose down -v
MEMORY_LIMIT=8g docker compose up -d timescaledb
sleep 20

# Valider connexion
PGPASSWORD=benchmark psql -h localhost -U postgres -d benchmark -c 'SELECT 1;'
```

### Diagnostic rapide

```bash
# 1) Docker OK
docker ps

# 2) Vérifier docker/.env
grep POSTGRES ~/baseTypeBenchmark/docker/.env

# 3) Vérifier ce que le conteneur a reçu
docker inspect -f '{{range .Config.Env}}{{println .}}{{end}}' btb_timescaledb | grep POSTGRES

# 4) Logs si problème
docker logs btb_timescaledb --tail 100

# 5) Valider cgroup/memory.peak
cd ~/baseTypeBenchmark
python3 scripts/diagnose_env.py --containers btb_timescaledb
```

### Lancer le smoke test P1

```bash
cd ~/baseTypeBenchmark
source .venv/bin/activate
python3 scripts/smoke_benchmark.py --profile small-2d --scenarios P1 --ram-levels 8 --n-warmup 1 --n-runs 1 --queries Q1
```

### Si erreur "non-transient" PostgreSQL

Le message d'erreur affiche maintenant :
- Les fichiers `.env` lus (ou "NONE FOUND")
- Le `repo_root` détecté
- Les actions correctives

Causes fréquentes :
1. `docker/.env` absent → `cp config/benchmark.env docker/.env`
2. Volume initialisé avec autres creds → `docker compose down -v`
3. Mismatch user (ex: `benchmark` vs `postgres`) → vérifier `docker/.env`
