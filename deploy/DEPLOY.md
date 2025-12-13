# Déploiement baseTypeBenchmark sur VPS OVH

## Prérequis

- Un VPS OVH (Ubuntu 22.04 ou Debian 12 recommandé)
- Minimum 4 Go RAM / 2 vCPU / 40 Go SSD
- VS Code avec extension Remote-SSH (Windows)
- Terminal Windows (PowerShell ou Windows Terminal)

## Étape 1 : Créer le VPS OVH

1. Aller sur [OVH Cloud](https://www.ovhcloud.com/fr/vps/)
2. Choisir un VPS Starter ou Essential :
   - **VPS Starter** : ~4€/mois (2 Go RAM) - OK pour profil `small`
   - **VPS Essential** : ~8€/mois (4 Go RAM) - Recommandé
3. OS : **Ubuntu 22.04** ou **Debian 12**
4. Noter l'IP et le mot de passe root

## Étape 2 : Connexion SSH depuis Windows

### Option A : Terminal Windows (PowerShell)
```powershell
ssh root@<IP_VPS>
```

### Option B : VS Code Remote-SSH
1. Installer l'extension "Remote - SSH"
2. `Ctrl+Shift+P` → "Remote-SSH: Connect to Host"
3. Entrer `root@<IP_VPS>`
4. Ouvrir le dossier `/opt/benchmark`

## Étape 3 : Setup du VPS (une seule fois)

```bash
# Sur le VPS, exécuter :
curl -fsSL https://raw.githubusercontent.com/synaptikad/baseTypeBenchmark/main/deploy/setup-vps.sh | sudo bash
```

Ou manuellement :
```bash
apt update && apt install -y git curl
cd /opt
git clone https://github.com/synaptikad/baseTypeBenchmark.git benchmark
cd benchmark
chmod +x deploy/*.sh
sudo ./deploy/setup-vps.sh
```

## Étape 4 : Lancer le benchmark

```bash
cd /opt/benchmark

# Benchmark complet profil "small"
./deploy/run-benchmark.sh small

# Autres profils disponibles :
./deploy/run-benchmark.sh medium
./deploy/run-benchmark.sh large
```

## Étape 5 : Récupérer les résultats

Les résultats sont dans `bench/results/` :
```bash
ls -la bench/results/
cat bench/results/*.json
```

### Copier les résultats sur Windows (depuis PowerShell)
```powershell
scp -r root@<IP_VPS>:/opt/benchmark/bench/results ./results
```

## Commandes utiles

```bash
# Voir les logs Docker en temps réel
docker compose logs -f

# État des services
docker compose ps

# Arrêter les services
docker compose down

# Supprimer toutes les données (reset complet)
docker compose down -v

# Relancer uniquement le benchmark (sans régénérer le dataset)
python3 -m bench.runner pg_rel
python3 -m bench.runner pg_jsonb
python3 -m bench.runner memgraph
python3 -m bench.runner oxigraph
```

## Utiliser Claude Code sur le VPS

Depuis ton terminal Windows avec Claude Code installé :

```powershell
# Se connecter au VPS et utiliser Claude Code
ssh root@<IP_VPS>
cd /opt/benchmark
# Claude Code fonctionne normalement via SSH
```

Ou utiliser VS Code Remote-SSH avec Claude Code extension.

## Troubleshooting

### Docker ne démarre pas
```bash
systemctl status docker
systemctl restart docker
```

### Service unhealthy
```bash
docker compose logs <service>
docker compose restart <service>
```

### Mémoire insuffisante
```bash
free -h
# Si < 2 Go disponible, augmenter le swap :
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
```

## Coûts estimés

| VPS OVH | RAM | Prix/mois | Profil recommandé |
|---------|-----|-----------|-------------------|
| Starter | 2 Go | ~4€ | small |
| Essential | 4 Go | ~8€ | small, medium |
| Comfort | 8 Go | ~16€ | medium, large |
