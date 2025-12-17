# BaseType Benchmark - Makefile

.PHONY: help install test demo dataset benchmark clean hf-check hf-login hf-publish hf-publish-dry hf-publish-custom

# Variables
PYTHON := python3
PIP := pip3
SRC_DIR := src
SCRIPT := $(SRC_DIR)/scripts/basetype_benchmark.py

# Couleurs pour les messages
GREEN := \033[0;32m
BLUE := \033[0;34m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Aide
help: ## Afficher cette aide
	@echo "$(BLUE)BaseType Benchmark - Système autonome$(NC)"
	@echo ""
	@echo "Commandes disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# Setup initial (nouvelle machine)
# Note: make doit etre installe manuellement d'abord:
#   sudo apt update && sudo apt install -y make
init: ## Setup initial complet (Docker, Python, deps)
	@echo "$(BLUE)Setup initial...$(NC)"
	@echo "Installation Docker et dependances systeme..."
	sudo apt update && sudo apt install -y docker.io docker-compose-v2 python3-pip python3-venv git
	sudo usermod -aG docker $$USER
	@echo "$(YELLOW)Reconnectez-vous ou executez: newgrp docker$(NC)"
	@echo "$(GREEN)Setup systeme termine. Executez ensuite: make install$(NC)"

# Installation
install: ## Installer les dépendances Python
	@echo "$(BLUE)Installation des dépendances...$(NC)"
	$(PIP) install -e .
	$(PIP) install -r requirements.txt

install-dev: ## Installer les dépendances de développement
	$(PIP) install -e ".[dev]"
	$(PIP) install -r requirements.txt

# Tests et validation
test: ## Exécuter les tests unitaires
	@echo "$(BLUE)Exécution des tests...$(NC)"
	$(PYTHON) -m pytest tests/ -v

test-integration: ## Tests d'intégration (nécessite Docker)
	@echo "$(YELLOW)Tests d'intégration (avec Docker)...$(NC)"
	$(PYTHON) -c "from basetype_benchmark.dataset.workflow import DatasetWorkflow; wf = DatasetWorkflow(); print('✅ Imports OK')"

demo: ## Démonstration de l'autonomie du système
	@echo "$(BLUE)Démonstration autonomie système...$(NC)"
	$(PYTHON) demo_autonomie.py

# Gestion des datasets
dataset-storage: ## Afficher l'état du stockage
	@echo "$(BLUE)État du stockage Codespace:$(NC)"
	$(PYTHON) $(SCRIPT) dataset storage

dataset-generate: ## Générer un dataset de test (small-1w)
	@echo "$(YELLOW)Génération dataset small-1w...$(NC)"
	$(PYTHON) $(SCRIPT) workflow session small-1w

dataset-sequential: ## Génération séquentielle automatique
	@echo "$(YELLOW)Démarrage génération séquentielle...$(NC)"
	@echo "$(RED)⚠️  Cette commande peut prendre du temps et utiliser de l'espace$(NC)"
	@read -p "Continuer ? (y/N) " confirm && [ "$$confirm" = "y" ] || exit 1
	$(PYTHON) $(SCRIPT) workflow sequential

# Benchmarks
benchmark-test: ## Test rapide (small-1w × postgres)
	@echo "$(YELLOW)Test benchmark rapide...$(NC)"
	$(PYTHON) $(SCRIPT) benchmark single small-1w postgres

benchmark-full: ## Suite complète de benchmarks (CONFIRMATION REQUISE)
	@echo "$(RED)🚨 SUITE COMPLÈTE DE BENCHMARKS$(NC)"
	@echo "$(RED)   • 108 tests combinaisons$(NC)"
	@echo "$(RED)   • Plusieurs heures d'exécution$(NC)"
	@echo "$(RED)   • Ressources Docker nécessaires$(NC)"
	@echo ""
	@read -p "Êtes-vous sûr de vouloir continuer ? (y/N) " confirm && [ "$$confirm" = "y" ] || exit 1
	@echo "$(BLUE)Démarrage suite complète...$(NC)"
	$(PYTHON) $(SCRIPT) benchmark full-suite

benchmark-list: ## Lister les profils de benchmark disponibles
	@echo "$(BLUE)Profils de benchmark disponibles:$(NC)"
	$(PYTHON) $(SCRIPT) benchmark list

# Benchmarks académiques séquentiels (nouveau workflow rigoureux)
benchmark-sequential-info: ## Afficher les profils compatibles pour workflow séquentiel
	@echo "$(BLUE)Profils compatibles workflow séquentiel académique:$(NC)"
	$(PYTHON) $(SRC_DIR)/scripts/run_sequential_benchmark.py info

benchmark-sequential-single: ## Benchmark séquentiel d'un profil (usage: make benchmark-sequential-single PROFILE=small-1w)
	@echo "$(YELLOW)Workflow séquentiel pour $(PROFILE)...$(NC)"
	$(PYTHON) $(SRC_DIR)/scripts/run_sequential_benchmark.py single $(PROFILE)

benchmark-sequential-suite: ## Suite séquentielle complète (5 profils × 3 paradigmes = 15 benchmarks)
	@echo "$(RED)🚨 SUITE SÉQUENTIELLE ACADÉMIQUE$(NC)"
	@echo "$(YELLOW)   • 5 profils × 3 paradigmes = 15 benchmarks$(NC)"
	@echo "$(YELLOW)   • Génération déterministe (seed=42)$(NC)"
	@echo "$(YELLOW)   • Tests séquentiels sur même dataset$(NC)"
	@echo "$(YELLOW)   • Plusieurs heures d'exécution$(NC)"
	@echo ""
	@read -p "Continuer ? (y/N) " confirm && [ "$$confirm" = "y" ] || exit 1
	@echo "$(BLUE)Démarrage suite séquentielle...$(NC)"
	$(PYTHON) $(SRC_DIR)/scripts/run_sequential_benchmark.py suite

# HuggingFace Hub (publication académique)
hf-check: ## Vérifier la configuration HuggingFace
	@echo "$(BLUE)Vérification HuggingFace...$(NC)"
	@$(PYTHON) -c "from basetype_benchmark.dataset.huggingface import check_dependencies; deps = check_dependencies(); print('huggingface_hub:', '✅' if deps['huggingface_hub'] else '❌'); print('pyarrow:', '✅' if deps['pyarrow'] else '❌')"
	@if [ -z "$$HF_TOKEN" ]; then echo "$(YELLOW)⚠️  HF_TOKEN non défini$(NC)"; else echo "$(GREEN)✅ HF_TOKEN configuré$(NC)"; fi

hf-login: ## Se connecter à HuggingFace (interactif)
	@echo "$(BLUE)Connexion à HuggingFace Hub...$(NC)"
	huggingface-cli login

hf-publish-dry: ## Générer le dataset sans publier (test local)
	@echo "$(YELLOW)Génération dataset pour HuggingFace (dry-run)...$(NC)"
	$(PYTHON) $(SRC_DIR)/scripts/publish_to_huggingface.py --profile=large-1y --skip-publish

hf-publish: ## Publier le dataset sur HuggingFace Hub
	@echo "$(RED)🚀 PUBLICATION SUR HUGGINGFACE HUB$(NC)"
	@echo "$(YELLOW)   • Profil: large-1y (dataset complet)$(NC)"
	@echo "$(YELLOW)   • Repo: synaptikad/basetype-benchmark$(NC)"
	@echo "$(YELLOW)   • Génération + upload$(NC)"
	@echo ""
	@if [ -z "$$HF_TOKEN" ]; then echo "$(RED)❌ HF_TOKEN requis. Configurez avec: export HF_TOKEN=hf_xxx$(NC)"; exit 1; fi
	@read -p "Publier sur HuggingFace ? (y/N) " confirm && [ "$$confirm" = "y" ] || exit 1
	$(PYTHON) $(SRC_DIR)/scripts/publish_to_huggingface.py --profile=large-1y

hf-publish-custom: ## Publier avec profil personnalisé (usage: make hf-publish-custom PROFILE=medium-1m)
	@echo "$(YELLOW)Publication profil $(PROFILE)...$(NC)"
	@if [ -z "$$HF_TOKEN" ]; then echo "$(RED)❌ HF_TOKEN requis$(NC)"; exit 1; fi
	$(PYTHON) $(SRC_DIR)/scripts/publish_to_huggingface.py --profile=$(PROFILE)

# Nettoyage
clean: ## Nettoyer les caches et fichiers temporaires
	@echo "$(YELLOW)Nettoyage des caches...$(NC)"
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name "*.cache" -delete
	@echo "$(GREEN)Nettoyage terminé$(NC)"

clean-data: ## Nettoyer les datasets générés (ATTENTION)
	@echo "$(RED)⚠️  Cette commande supprime TOUS les datasets générés$(NC)"
	@read -p "Continuer ? (y/N) " confirm && [ "$$confirm" = "y" ] || exit 1
	rm -rf data/
	@echo "$(GREEN)Datasets supprimés$(NC)"

# Docker
docker-build: ## Construire les images Docker
	@echo "$(BLUE)Construction images Docker...$(NC)"
	cd docker && docker-compose build

docker-up: ## Démarrer les services Docker
	@echo "$(BLUE)Démarrage services Docker...$(NC)"
	cd docker && docker-compose up -d

docker-down: ## Arrêter les services Docker
	@echo "$(BLUE)Arrêt services Docker...$(NC)"
	cd docker && docker-compose down

docker-logs: ## Afficher les logs Docker
	cd docker && docker-compose logs -f

# Développement
lint: ## Vérifier le style du code
	@echo "$(BLUE)Vérification du code...$(NC)"
	$(PYTHON) -m black --check src/
	$(PYTHON) -m isort --check-only src/

format: ## Formatter le code
	@echo "$(BLUE)Formatage du code...$(NC)"
	$(PYTHON) -m black src/
	$(PYTHON) -m isort src/

# Informations système
info: ## Informations sur le système
	@echo "$(BLUE)Informations système:$(NC)"
	@echo "Python: $$(python3 --version)"
	@echo "Docker: $$(docker --version 2>/dev/null || echo 'Non installé')"
	@echo "Espace disque: $$(df -h . | tail -1 | awk '{print $$4 \" libres\"}')"
	@echo ""
	@echo "$(BLUE)État du projet:$(NC)"
	@ls -la | grep -E "\.(md|txt|toml)$$" | while read line; do echo "  $$line"; done

# Raccourcis pratiques
setup: install docker-build ## Installation complète
	@echo "$(GREEN)Installation terminée !$(NC)"
	@echo "Utilisez 'make demo' pour voir l'autonomie du système"

quick-start: dataset-storage dataset-generate benchmark-test ## Démarrage rapide (test complet)
	@echo "$(GREEN)Démarrage rapide terminé !$(NC)"

# Sécurité
check-security: ## Vérifications de sécurité basiques
	@echo "$(BLUE)Vérifications de sécurité...$(NC)"
	@echo "🔍 Recherche de mots de passe en dur..."
	@grep -r "password\|token\|secret" --include="*.py" src/ || echo "✅ Aucun mot de passe trouvé"
	@echo "🔍 Recherche de clés API..."
	@grep -r "api_key\|API_KEY" --include="*.py" src/ || echo "✅ Aucune clé API en dur"

# Documentation
docs: ## Générer la documentation
	@echo "$(BLUE)Génération documentation...$(NC)"
	@echo "📖 README principal: README.md"
	@echo "📖 Docs dataset: src/basetype_benchmark/dataset/README.md"
	@echo "🔗 Structure du code dans les docstrings"

# Alias pour compatibilité
all: help
.DEFAULT_GOAL := help
