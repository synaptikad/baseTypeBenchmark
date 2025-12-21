# Spécification de Refactoring - BaseType Benchmark

## État des lieux (après rollback)

### Analyse du code actuel

Le fichier `run.py` contient **4192 lignes** organise en blocs fonctionnels :

```
run.py (4192 lignes)
├── SECTION: Imports & Constants           # 1-60
├── SECTION: Helper Functions              # 61-156
│   ├── print_header, print_ok, print_err
│   ├── prompt, prompt_yes_no
│   └── run_cmd, _report_load_progress
├── SECTION: Docker Compose Detection      # 124-156
├── SECTION: Configuration                 # 158-207
│   ├── SCENARIOS (P1, P2, M1, M2, O1, O2)
│   ├── SCALES (small, medium, large)
│   ├── DURATIONS (2d, 1w, 1m, 6m, 1y)
│   └── SIZE_ESTIMATES
├── SECTION: HuggingFace Download          # 209-275
├── SECTION: Container Management          # 277-397
│   ├── stop_all_containers
│   ├── start_containers
│   ├── check_dataset
│   ├── get_available_profiles
│   └── get_scenario_files
├── SECTION: Workflow Dataset              # 399-527
├── SECTION: RAM Configuration             # 529-961
│   ├── RAM_LEVELS, MIN_RAM_BY_SCALE
│   ├── get_ram_strategy
│   ├── start_containers_with_ram
│   ├── get_container_stats (CLI parsing)
│   ├── get_container_cgroup_path
│   ├── get_cgroup_metrics
│   ├── CGroupMetricsSnapshot (class)
│   ├── check_container_oom
│   ├── get_container_logs
│   ├── dump_container_debug
│   ├── drop_caches
│   ├── get_container_io_stats (CLI parsing)
│   └── ResourceMonitor (class)
├── SECTION: Benchmark Execution Engine    # 1144-1499
│   ├── QUERIES_BY_SCENARIO
│   ├── HYBRID_QUERY_TYPE
│   ├── PROTOCOL_CONFIG
│   ├── QUERY_PARAMS
│   ├── get_query_variants
│   ├── substitute_params
│   ├── load_query, load_ts_query
│   ├── extract_point_ids_from_graph_result
│   ├── compute_stats
│   ├── print_query_result
│   └── print_benchmark_summary
├── SECTION: Query Benchmark Functions     # 1500-1886
│   ├── extract_dataset_info
│   ├── run_query_benchmark
│   └── run_query_with_variants
├── SECTION: Scenario Runners              # 1889-3073
│   ├── run_scenario_benchmark
│   ├── _run_postgres_benchmark
│   ├── _load_postgres_from_csv
│   ├── _load_memgraph_nodes_csv
│   ├── _load_memgraph_edges_csv
│   ├── _load_memgraph_chunks_csv
│   ├── run_hybrid_query
│   ├── _run_memgraph_benchmark
│   └── _run_oxigraph_benchmark
├── SECTION: RAM Gradient Protocol         # 3076-3197
│   ├── run_ram_gradient_benchmark
│   └── _next_ram_level
├── SECTION: Subset Extraction             # 3199-3278
│   ├── get_master_dataset
│   ├── get_extractable_configs
│   └── ensure_dataset_extracted
├── SECTION: Benchmark Workflow            # 3281-3933
│   ├── select_ram_levels
│   ├── workflow_benchmark
│   ├── _run_full_benchmark
│   ├── _run_quick_benchmark
│   ├── _run_selective_benchmark
│   ├── _find_resumable_campaigns
│   ├── _run_resume_benchmark
│   ├── _run_custom_ram_gradient
│   ├── _save_full_results
│   ├── _print_quick_summary
│   └── _print_ram_gradient_summary
├── SECTION: Workflow Publish              # 3935-4005
└── SECTION: Workflow Purge & Main         # 4006-4192
```

### Métriques du code actuel

| Métrique | Valeur | Recommandé |
|----------|--------|------------|
| Lignes de code | 4192 | < 500/fichier |
| Fonctions | ~85 | < 20/fichier |
| Classes | 2 (CGroupMetricsSnapshot, ResourceMonitor) | - |
| Niveaux d'indentation max | 6-7 | < 4 |
| Responsabilités mélangées | Oui | Non |

### Points critiques identifiés

1. **Docker stats via CLI** (lignes 693-726, 963-1015)
   - Parsing fragile de `docker stats --format`
   - Susceptible aux variations de format
   - Doit être remplacé par `docker-py`

2. **Chargement de données dans run.py** (lignes 2077-2478)
   - `_load_postgres_from_csv` : 207 lignes
   - `_load_memgraph_nodes_csv` : 53 lignes
   - `_load_memgraph_edges_csv` : 44 lignes
   - `_load_memgraph_chunks_csv` : 86 lignes
   - Devrait être dans `loaders/`

3. **Fédération Graph→TimescaleDB** (lignes 2481-2617)
   - `run_hybrid_query` : 137 lignes
   - Injection d'IDs via `ARRAY[...]` - ne scale pas
   - Manque de gestion des gros volumes (tables temporaires)

4. **Duplication des runners** (lignes 1956-3073)
   - `_run_postgres_benchmark` : 118 lignes
   - `_run_memgraph_benchmark` : 226 lignes
   - `_run_oxigraph_benchmark` : 225 lignes
   - Même structure répétée 3 fois

---

## Modules existants (ne pas toucher)

Les modules suivants sont déjà bien structurés :

```
src/basetype_benchmark/
├── benchmark/
│   ├── resource_monitor.py     # ExtendedResourceMonitor, DockerStatsCollector
│   ├── metrics.py
│   ├── checkpoint.py
│   ├── ram_config.py
│   └── config.py
├── dataset/
│   ├── generator_v2.py         # Génération avec simulation physique
│   ├── exporter_v2.py          # Export 6 formats
│   ├── dataset_manager.py
│   ├── subset_extractor.py
│   ├── huggingface.py
│   └── simulation/             # Moteur de simulation
├── loaders/
│   ├── postgres/load.py        # get_connection, clear_database, etc.
│   ├── memgraph/load.py        # get_driver, LoadingTimeout, LoadingStalled
│   └── oxigraph/load.py        # wait_for_oxigraph, load_ntriples, etc.
```

---

## Architecture Cible

### Nouveaux modules à créer

```
src/basetype_benchmark/
├── cli/                          # Interface utilisateur (NOUVEAU)
│   ├── __init__.py
│   ├── main.py                   # Point d'entrée, menu principal
│   ├── formatters.py             # print_ok, print_err, couleurs ANSI
│   └── prompts.py                # prompt, prompt_yes_no
│
├── runners/                      # Exécution des benchmarks (NOUVEAU)
│   ├── __init__.py
│   ├── base.py                   # Classe abstraite BenchmarkRunner
│   ├── postgres.py               # PostgresRunner (P1, P2)
│   ├── memgraph.py               # MemgraphRunner (M1, M2)
│   ├── oxigraph.py               # OxigraphRunner (O1, O2)
│   └── hybrid.py                 # HybridQueryExecutor (fédération)
│
├── infrastructure/               # Gestion Docker (NOUVEAU)
│   ├── __init__.py
│   ├── docker_manager.py         # docker-py API au lieu de CLI
│   ├── cgroup_monitor.py         # Métriques cgroups v2
│   └── ram_controller.py         # RAM gradient, memory limits
│
├── queries/                      # Gestion des requêtes (NOUVEAU)
│   ├── __init__.py
│   ├── loader.py                 # load_query, load_ts_query
│   ├── variants.py               # get_query_variants, substitution
│   └── federation.py             # Fédération scalable avec tables temp
│
├── workflows/                    # Orchestration haut niveau (NOUVEAU)
│   ├── __init__.py
│   ├── dataset.py                # workflow_dataset
│   ├── benchmark.py              # workflow_benchmark
│   ├── publish.py                # workflow_publish
│   └── purge.py                  # workflow_purge
│
└── config/                       # Configuration centralisée (NOUVEAU)
    ├── __init__.py
    ├── profiles.py               # SCALES, DURATIONS, SIZE_ESTIMATES
    ├── scenarios.py              # SCENARIOS, containers par scénario
    └── protocol.py               # PROTOCOL_CONFIG, QUERY_PARAMS
```

---

## Spécifications Détaillées

### 1. Module `infrastructure/docker_manager.py`

Remplace les appels CLI Docker par l'API docker-py.

```python
"""Docker container management via Python API."""
import docker
from docker.errors import NotFound, APIError
from typing import Dict, List, Optional
import time


class DockerManager:
    """Gestion des containers Docker via l'API Python.

    Remplace les appels subprocess à docker CLI pour :
    - Meilleure fiabilité (pas de parsing de sortie)
    - Meilleure performance (pas de fork)
    - Meilleure gestion d'erreurs
    """

    def __init__(self):
        self.client = docker.from_env()
        self._compose_project = "btb"

    def start_container(
        self,
        name: str,
        image: str,
        ports: Dict[str, int],
        environment: Dict[str, str] = None,
        mem_limit: str = None,
        volumes: Dict[str, Dict] = None,
        healthcheck_port: int = None
    ) -> bool:
        """Démarre un container avec les paramètres spécifiés.

        Args:
            name: Nom du container (ex: "btb_timescaledb")
            image: Image Docker (ex: "timescale/timescaledb-ha:pg16")
            ports: Mapping ports {container_port: host_port}
            environment: Variables d'environnement
            mem_limit: Limite mémoire (ex: "8g", "4096m")
            volumes: Volumes à monter
            healthcheck_port: Port pour vérifier que le service est prêt

        Returns:
            True si le container est démarré et prêt
        """
        try:
            # Arrêter si existant
            self.stop_container(name)

            # Créer et démarrer
            container = self.client.containers.run(
                image=image,
                name=name,
                ports=ports,
                environment=environment or {},
                mem_limit=mem_limit,
                volumes=volumes or {},
                detach=True,
                auto_remove=False
            )

            # Attendre que le service soit prêt
            if healthcheck_port:
                return self._wait_for_port(healthcheck_port, timeout=60)
            return self._wait_running(name, timeout=30)

        except APIError as e:
            print(f"Docker API error: {e}")
            return False

    def stop_container(self, name: str) -> bool:
        """Arrête et supprime un container."""
        try:
            container = self.client.containers.get(name)
            container.stop(timeout=10)
            container.remove(force=True)
            return True
        except NotFound:
            return True  # Déjà arrêté
        except APIError as e:
            print(f"Error stopping {name}: {e}")
            return False

    def get_container_stats(self, name: str) -> Optional[Dict]:
        """Récupère les stats d'un container via l'API (pas de CLI parsing).

        Returns:
            Dict avec memory_usage_mb, memory_limit_mb, cpu_percent,
            network_rx_bytes, network_tx_bytes, block_read_bytes, block_write_bytes
        """
        try:
            container = self.client.containers.get(name)
            stats = container.stats(stream=False)

            memory_stats = stats.get("memory_stats", {})
            cpu_stats = stats.get("cpu_stats", {})
            precpu_stats = stats.get("precpu_stats", {})

            # Calcul CPU
            cpu_delta = (
                cpu_stats.get("cpu_usage", {}).get("total_usage", 0) -
                precpu_stats.get("cpu_usage", {}).get("total_usage", 0)
            )
            system_delta = (
                cpu_stats.get("system_cpu_usage", 0) -
                precpu_stats.get("system_cpu_usage", 0)
            )
            cpu_count = len(cpu_stats.get("cpu_usage", {}).get("percpu_usage", [1]))

            cpu_percent = 0.0
            if system_delta > 0 and cpu_delta > 0:
                cpu_percent = (cpu_delta / system_delta) * cpu_count * 100.0

            # I/O
            blkio = stats.get("blkio_stats", {}).get("io_service_bytes_recursive", [])
            block_read = sum(b.get("value", 0) for b in blkio if b.get("op") == "read")
            block_write = sum(b.get("value", 0) for b in blkio if b.get("op") == "write")

            # Network
            networks = stats.get("networks", {})
            net_rx = sum(n.get("rx_bytes", 0) for n in networks.values())
            net_tx = sum(n.get("tx_bytes", 0) for n in networks.values())

            return {
                "memory_usage_mb": memory_stats.get("usage", 0) / (1024 * 1024),
                "memory_limit_mb": memory_stats.get("limit", 0) / (1024 * 1024),
                "memory_percent": (
                    memory_stats.get("usage", 0) / memory_stats.get("limit", 1) * 100
                    if memory_stats.get("limit") else 0
                ),
                "cpu_percent": cpu_percent,
                "network_rx_bytes": net_rx,
                "network_tx_bytes": net_tx,
                "block_read_bytes": block_read,
                "block_write_bytes": block_write,
            }
        except NotFound:
            return None
        except APIError:
            return None

    def is_running(self, name: str) -> bool:
        """Vérifie si un container est en cours d'exécution."""
        try:
            container = self.client.containers.get(name)
            return container.status == "running"
        except NotFound:
            return False

    def check_oom_killed(self, name: str) -> bool:
        """Vérifie si un container a été tué par OOM."""
        try:
            container = self.client.containers.get(name)
            return container.attrs.get("State", {}).get("OOMKilled", False)
        except NotFound:
            return False

    def get_logs(self, name: str, tail: int = 100) -> str:
        """Récupère les logs d'un container."""
        try:
            container = self.client.containers.get(name)
            return container.logs(tail=tail).decode("utf-8")
        except NotFound:
            return ""

    def _wait_running(self, name: str, timeout: int = 30) -> bool:
        """Attend qu'un container soit en état running."""
        start = time.time()
        while time.time() - start < timeout:
            if self.is_running(name):
                return True
            time.sleep(1)
        return False

    def _wait_for_port(self, port: int, timeout: int = 60) -> bool:
        """Attend qu'un port soit accessible."""
        import socket
        start = time.time()
        while time.time() - start < timeout:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    s.connect(("localhost", port))
                    return True
            except (socket.error, socket.timeout):
                time.sleep(1)
        return False
```

---

### 2. Module `queries/federation.py`

Gère la fédération Graph→TimescaleDB de manière scalable.

```python
"""Scalable federation handler for Graph → TimescaleDB queries.

For hybrid scenarios (M2, O2), graph queries return point_ids that need
to be passed to TimescaleDB for timeseries aggregation.

Problem: ARRAY[id1, id2, ...] syntax doesn't scale beyond ~10k IDs.
Solution: Use temp tables for large ID sets.
"""
from typing import List, Dict, Iterator, Optional
import time


class FederationHandler:
    """Gère la fédération Graph → TimescaleDB de manière scalable.

    Stratégies selon le volume d'IDs:
    - < 10,000 IDs : injection directe via ARRAY[...]
    - >= 10,000 IDs : table temporaire avec COPY
    """

    BATCH_THRESHOLD = 10000
    COPY_BATCH_SIZE = 5000

    def __init__(self, pg_connection):
        self.pg_conn = pg_connection

    def execute_federated_query(
        self,
        point_ids: List[str],
        ts_query_template: str,
        params: Dict = None
    ) -> tuple[List[Dict], float]:
        """Exécute une requête fédérée de manière scalable.

        Args:
            point_ids: Liste des IDs à passer à TimescaleDB
            ts_query_template: Template SQL avec placeholder $POINT_IDS
            params: Paramètres additionnels (dates, etc.)

        Returns:
            Tuple (résultats, temps_ms)
        """
        if not point_ids:
            return [], 0.0

        start = time.perf_counter()

        if len(point_ids) < self.BATCH_THRESHOLD:
            results = self._execute_with_array(point_ids, ts_query_template, params)
        else:
            results = self._execute_with_temp_table(point_ids, ts_query_template, params)

        elapsed_ms = (time.perf_counter() - start) * 1000
        return results, elapsed_ms

    def _execute_with_array(
        self,
        point_ids: List[str],
        query_template: str,
        params: Dict = None
    ) -> List[Dict]:
        """Injection directe via ARRAY (< 10k IDs)."""
        # Construire ARRAY literal
        ids_literal = "ARRAY[" + ",".join(f"'{pid}'" for pid in point_ids) + "]"
        query = query_template.replace("$POINT_IDS", ids_literal)

        # Substituer les autres paramètres
        if params:
            for key, value in params.items():
                placeholder = f"${key.upper()}"
                if isinstance(value, str):
                    query = query.replace(placeholder, f"'{value}'")
                else:
                    query = query.replace(placeholder, str(value))

        cursor = self.pg_conn.cursor()
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        self.pg_conn.commit()
        cursor.close()

        return results

    def _execute_with_temp_table(
        self,
        point_ids: List[str],
        query_template: str,
        params: Dict = None
    ) -> List[Dict]:
        """Utilise une table temporaire (>= 10k IDs).

        Stratégie:
        1. CREATE TEMP TABLE _fed_ids (point_id TEXT) ON COMMIT DROP
        2. INSERT par batch de 5000
        3. Remplacer $POINT_IDS par sous-requête
        4. Exécuter et retourner résultats
        """
        cursor = self.pg_conn.cursor()

        try:
            # 1. Créer table temporaire
            cursor.execute("""
                CREATE TEMP TABLE IF NOT EXISTS _fed_point_ids (
                    point_id TEXT PRIMARY KEY
                ) ON COMMIT DROP
            """)
            cursor.execute("TRUNCATE _fed_point_ids")

            # 2. Insérer par batch (plus efficace que INSERT VALUES)
            from io import StringIO
            buffer = StringIO()
            for pid in point_ids:
                buffer.write(f"{pid}\n")
            buffer.seek(0)

            cursor.copy_from(buffer, "_fed_point_ids", columns=["point_id"])

            # 3. Modifier la requête pour utiliser la table temp
            # Remplacer $POINT_IDS par une sous-requête
            query = query_template.replace(
                "$POINT_IDS",
                "(SELECT point_id FROM _fed_point_ids)"
            )

            # Adapter la syntaxe: WHERE point_id = ANY($POINT_IDS)
            # devient: WHERE point_id IN (SELECT point_id FROM _fed_point_ids)
            query = query.replace("= ANY(", "IN (")

            # Substituer les autres paramètres
            if params:
                for key, value in params.items():
                    placeholder = f"${key.upper()}"
                    if isinstance(value, str):
                        query = query.replace(placeholder, f"'{value}'")
                    else:
                        query = query.replace(placeholder, str(value))

            # 4. Exécuter
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

            self.pg_conn.commit()
            return results

        except Exception as e:
            self.pg_conn.rollback()
            raise
        finally:
            cursor.close()

    def stream_federated_query(
        self,
        point_ids_iterator: Iterator[str],
        ts_query_template: str,
        params: Dict = None,
        batch_size: int = 5000
    ) -> Iterator[Dict]:
        """Version streaming pour très gros volumes.

        Traite les IDs par batch et yield les résultats progressivement.
        Utile pour large-1y avec millions de points.
        """
        batch = []

        for point_id in point_ids_iterator:
            batch.append(point_id)

            if len(batch) >= batch_size:
                results, _ = self.execute_federated_query(batch, ts_query_template, params)
                yield from results
                batch = []

        # Dernier batch
        if batch:
            results, _ = self.execute_federated_query(batch, ts_query_template, params)
            yield from results
```

---

### 3. Module `runners/base.py`

Classe abstraite pour les runners de benchmark.

```python
"""Abstract base runner for benchmark execution."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any
import time


@dataclass
class QueryResult:
    """Résultat d'une exécution de requête."""
    query_id: str
    latencies_ms: List[float] = field(default_factory=list)
    row_count: int = 0
    success: bool = True
    error: Optional[str] = None
    params: Dict = field(default_factory=dict)


@dataclass
class LoadResult:
    """Résultat du chargement de données."""
    nodes_count: int = 0
    edges_count: int = 0
    timeseries_count: int = 0
    chunks_count: int = 0
    duration_s: float = 0.0
    peak_memory_mb: float = 0.0


@dataclass
class BenchmarkResult:
    """Résultat complet d'un benchmark."""
    scenario: str
    profile: str
    status: str = "pending"  # pending, completed, error, oom, stalled
    load_result: Optional[LoadResult] = None
    query_results: Dict[str, QueryResult] = field(default_factory=dict)
    load_time_s: float = 0.0
    query_time_s: float = 0.0
    total_time_s: float = 0.0
    ram_gb: Optional[int] = None
    error: Optional[str] = None
    system_info: Dict = field(default_factory=dict)


class BenchmarkRunner(ABC):
    """Interface commune pour tous les runners de benchmark.

    Template Method pattern : run_benchmark() définit le squelette,
    les sous-classes implémentent les étapes spécifiques.
    """

    def __init__(self, scenario: str, export_dir: Path, profile: str):
        self.scenario = scenario
        self.export_dir = export_dir
        self.profile = profile

    @property
    @abstractmethod
    def container_name(self) -> str:
        """Nom du container Docker principal."""
        pass

    @property
    @abstractmethod
    def supported_scenarios(self) -> List[str]:
        """Liste des scénarios supportés (ex: ['P1', 'P2'])."""
        pass

    @abstractmethod
    def connect(self) -> None:
        """Établit la connexion à la base de données."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Ferme la connexion."""
        pass

    @abstractmethod
    def clear_data(self) -> None:
        """Vide la base de données."""
        pass

    @abstractmethod
    def load_data(self) -> LoadResult:
        """Charge les données. Retourne stats de chargement."""
        pass

    @abstractmethod
    def execute_query(self, query: str) -> tuple[int, float]:
        """Exécute une requête.

        Returns:
            Tuple (row_count, latency_ms)
        """
        pass

    def run_benchmark(
        self,
        queries: List[str],
        n_warmup: int,
        n_runs: int,
        query_loader: callable = None
    ) -> BenchmarkResult:
        """Exécute le benchmark complet (template method).

        Args:
            queries: Liste des query IDs à exécuter (Q1, Q2, ...)
            n_warmup: Nombre d'itérations de warmup
            n_runs: Nombre d'itérations mesurées
            query_loader: Fonction pour charger le texte d'une requête
        """
        result = BenchmarkResult(
            scenario=self.scenario,
            profile=self.profile
        )

        start_total = time.time()

        try:
            # 1. Connect
            self.connect()

            # 2. Clear
            self.clear_data()

            # 3. Load data
            start_load = time.time()
            result.load_result = self.load_data()
            result.load_time_s = time.time() - start_load

            # 4. Execute queries
            start_query = time.time()
            for query_id in queries:
                query_text = query_loader(self.scenario, query_id) if query_loader else None
                if not query_text:
                    continue

                qr = self._run_query_with_protocol(
                    query_id, query_text, n_warmup, n_runs
                )
                result.query_results[query_id] = qr

            result.query_time_s = time.time() - start_query
            result.status = "completed"

        except Exception as e:
            result.status = "error"
            result.error = str(e)

        finally:
            self.disconnect()
            result.total_time_s = time.time() - start_total

        return result

    def _run_query_with_protocol(
        self,
        query_id: str,
        query_text: str,
        n_warmup: int,
        n_runs: int
    ) -> QueryResult:
        """Exécute une requête selon le protocole (warmup + runs)."""
        qr = QueryResult(query_id=query_id)

        try:
            # Warmup (résultats ignorés)
            for _ in range(n_warmup):
                self.execute_query(query_text)

            # Measured runs
            for _ in range(n_runs):
                rows, latency = self.execute_query(query_text)
                qr.latencies_ms.append(latency)
                qr.row_count = rows

            qr.success = True

        except Exception as e:
            qr.success = False
            qr.error = str(e)

        return qr
```

---

## Plan de Migration

### Phase 1 : Infrastructure (2-3 jours)

1. **Créer `infrastructure/docker_manager.py`**
   - Installer `docker` dans requirements.txt
   - Implémenter DockerManager avec docker-py
   - Tester avec les 3 containers

2. **Créer `infrastructure/ram_controller.py`**
   - Extraire la logique RAM gradient de run.py
   - Tester les limites mémoire

3. **Mise à jour progressive de run.py**
   - Remplacer `get_container_stats` par `DockerManager.get_container_stats`
   - Garder l'ancien code commenté jusqu'à validation

### Phase 2 : Runners (3-4 jours)

1. **Créer `runners/base.py`**
   - Définir BenchmarkRunner, QueryResult, LoadResult

2. **Créer `runners/postgres.py`**
   - Migrer `_run_postgres_benchmark`
   - Migrer `_load_postgres_from_csv`

3. **Créer `runners/memgraph.py`**
   - Migrer `_run_memgraph_benchmark`
   - Migrer les loaders CSV

4. **Créer `runners/oxigraph.py`**
   - Migrer `_run_oxigraph_benchmark`

### Phase 3 : Queries & Federation (2 jours)

1. **Créer `queries/federation.py`**
   - Implémenter FederationHandler
   - Ajouter support tables temporaires

2. **Créer `queries/loader.py`**
   - Migrer `load_query`, `load_ts_query`
   - Migrer `substitute_params`

### Phase 4 : CLI & Workflows (2 jours)

1. **Créer `cli/` module**
   - Séparer formatters et prompts
   - Créer le point d'entrée principal

2. **Créer `workflows/`**
   - Migrer les 4 workflows
   - Garder la logique métier intacte

### Phase 5 : Nettoyage (1 jour)

1. **Supprimer run.py monolithique**
2. **Mettre à jour les imports**
3. **Mettre à jour la documentation**

---

## Dépendances à ajouter

```toml
# pyproject.toml
[project.dependencies]
docker = ">=6.0.0"  # API Docker Python
```

---

## Tests

### Structure

```
tests/
├── unit/
│   ├── test_docker_manager.py
│   ├── test_federation.py
│   └── test_runners/
│       ├── test_postgres_runner.py
│       ├── test_memgraph_runner.py
│       └── test_oxigraph_runner.py
├── integration/
│   ├── test_full_benchmark.py
│   └── test_hybrid_queries.py
└── fixtures/
    └── sample_data/
```

---

## Critères de Succès

| Critère | Métrique | Cible |
|---------|----------|-------|
| Lignes par fichier | LOC | < 500 |
| Couverture tests | % | > 80% |
| Couplage | Dépendances cycliques | 0 |
| Temps de migration | Jours | < 15 |
| Régressions | Tests cassés | 0 |
| Performance | Overhead | < 5% |

---

## Validation

```bash
# Créer la structure
mkdir -p src/basetype_benchmark/{cli,runners,infrastructure,queries,workflows,config}

# Test syntaxe après chaque modification
python -m py_compile src/basetype_benchmark/infrastructure/docker_manager.py

# Test unitaires
pytest tests/unit/ -v

# Test intégration (benchmark complet small-1w)
python run.py  # Menu interactif
```
