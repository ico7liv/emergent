#!/bin/bash

# Script d'installation et configuration pour le monitoring Binance

echo "🚀 Installation du monitoring Binance..."

# Installer les dépendances Python
echo "📦 Installation de requests..."
pip3 install requests

# Rendre le script exécutable
chmod +x binance_monitor_simple.py

echo "✅ Installation terminée!"
echo ""
echo "📝 Configuration du CRON pour exécution toutes les 15 minutes:"
echo "Ajoutez cette ligne à votre crontab (crontab -e) :"
echo ""
echo "*/15 * * * * /usr/bin/python3 /path/to/binance_monitor_simple.py >> /var/log/binance_monitor.log 2>&1"
echo ""
echo "Remplacez '/path/to/' par le chemin complet vers votre script."
echo ""
echo "🔧 Pour tester le script immédiatement:"
echo "python3 binance_monitor_simple.py"
echo ""
echo "📊 Pour voir les logs:"
echo "tail -f /var/log/binance_monitor.log"