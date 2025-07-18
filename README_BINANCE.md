# Script de Monitoring Binance

## Description
Ce script surveille les annonces Binance pour détecter les nouveaux launchpools et airdrops hodler, puis envoie des alertes via Telegram.

## Fonctionnalités
- ✅ Surveillance automatique des annonces Binance
- ✅ Détection des mots-clés "binance launchpool" et "binance hodler"
- ✅ Alertes Telegram instantanées
- ✅ Système anti-doublon avec fichier texte
- ✅ Logs détaillés
- ✅ Méthodes de récupération multiples (API + RSS)

## Installation

1. **Copier les fichiers sur votre VPS:**
   ```bash
   # Copier binance_monitor.py sur votre VPS
   # Copier install_binance_monitor.sh sur votre VPS
   ```

2. **Installer les dépendances:**
   ```bash
   chmod +x install_binance_monitor.sh
   ./install_binance_monitor.sh
   ```

3. **Configurer le CRON:**
   ```bash
   crontab -e
   ```
   Ajouter cette ligne pour exécution toutes les 15 minutes:
   ```
   */15 * * * * /usr/bin/python3 /path/to/binance_monitor.py >> /var/log/binance_monitor.log 2>&1
   ```

## Configuration Telegram
Le script utilise déjà votre configuration Telegram. Les paramètres sont dans le code:
- Bot Token: `1142206850:AAHz9Cw6nKxzT6j1Mh1s4kLYSDj7jAZih1c`
- Chat ID: `453473151`

## Fichiers générés
- `seen_articles.txt` : Liste des articles déjà traités
- `/var/log/binance_monitor.log` : Logs d'exécution

## Test manuel
```bash
python3 binance_monitor.py
```

## Surveillance des logs
```bash
# Voir les derniers logs
tail -f /var/log/binance_monitor.log

# Voir les articles vus
cat seen_articles.txt
```

## Fonctionnement
1. Le script récupère les annonces via l'API Binance
2. En cas d'échec, il utilise le flux RSS
3. Il filtre les titres contenant "binance launchpool" ou "binance hodler"
4. Il compare avec les articles déjà vus (seen_articles.txt)
5. Il envoie une alerte Telegram pour chaque nouvel article détecté
6. Il sauvegarde les nouveaux articles dans le fichier texte

## Exemple d'alerte Telegram
```
🚀 NOUVEAU LAUNCHPOOL DÉTECTÉ!

📢 Binance Launchpool Announces New Token XYZ

🔗 https://www.binance.com/en/support/announcement/list/48

⏰ 2025-07-18 16:30:00
```