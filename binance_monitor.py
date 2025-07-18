#!/usr/bin/env python3
"""
Script de surveillance des annonces Binance
Surveille les nouveaux launchpools et airdrops hodler
Envoie des alertes Telegram et évite les doublons
"""

import requests
import json
import os
import re
from datetime import datetime
from urllib.parse import quote_plus

def send_telegram_alert(message):
    """Envoie une alerte Telegram"""
    try:
        # Configuration Telegram (à adapter avec vos credentials)
        url_telegram = "https://api.telegram.org/bot1142206850:AAHz9Cw6nKxzT6j1Mh1s4kLYSDj7jAZih1c/sendMessage?chat_id=453473151&text="
        
        # Encode le message pour l'URL
        encoded_message = quote_plus(message)
        url_push_telegram = url_telegram + encoded_message
        
        print("ALERT")
        print(f"Envoi du message: {message}")
        
        response = requests.get(url_push_telegram, timeout=30)
        
        if response.status_code == 200:
            print("✅ Message Telegram envoyé avec succès")
        else:
            print(f"❌ Erreur envoi Telegram: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi Telegram: {e}")

def load_seen_articles(filename="seen_articles.txt"):
    """Charge la liste des articles déjà vus"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return set(line.strip() for line in f if line.strip())
        return set()
    except Exception as e:
        print(f"❌ Erreur lecture fichier: {e}")
        return set()

def save_seen_articles(seen_articles, filename="seen_articles.txt"):
    """Sauvegarde la liste des articles vus"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for article_id in sorted(seen_articles):
                f.write(f"{article_id}\n")
        print(f"✅ {len(seen_articles)} articles sauvegardés")
    except Exception as e:
        print(f"❌ Erreur sauvegarde: {e}")

def get_binance_announcements():
    """Récupère les annonces Binance via l'API officielle"""
    try:
        # Méthode 1: API Binance officielle
        api_url = "https://www.binance.com/bapi/composite/v1/public/cms/article/catalog/list/query"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
            'Content-Type': 'application/json',
            'Origin': 'https://www.binance.com',
            'Referer': 'https://www.binance.com/en/support/announcement/list/48'
        }
        
        # Payload pour récupérer les annonces (catalogue 48 = Product Launch)
        payload = {
            "catalogId": 48,
            "pageNo": 1,
            "pageSize": 15
        }
        
        print(f"🔍 Récupération des annonces via API Binance...")
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('code') == '000000' and 'data' in data:
                articles = data['data'].get('articles', [])
                print(f"✅ {len(articles)} articles récupérés via API")
                return articles
            else:
                print(f"❌ Erreur API: {data.get('message', 'Code: ' + str(data.get('code')))}")
        else:
            print(f"❌ Erreur HTTP API: {response.status_code}")
            
        # Méthode 2: Fallback vers RSS
        return get_binance_announcements_rss()
            
    except Exception as e:
        print(f"❌ Erreur API: {e}")
        return get_binance_announcements_rss()

def get_binance_announcements_rss():
    """Méthode de fallback via RSS"""
    try:
        print("🔄 Tentative via RSS Binance...")
        
        rss_url = "https://www.binance.com/en/rss/announcements"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml'
        }
        
        response = requests.get(rss_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            # Parse basique du XML RSS
            content = response.text
            
            # Regex pour extraire les titres des articles
            title_pattern = r'<title><!\[CDATA\[(.*?)\]\]></title>'
            titles = re.findall(title_pattern, content)
            
            # Regex pour extraire les dates
            date_pattern = r'<pubDate>(.*?)</pubDate>'
            dates = re.findall(date_pattern, content)
            
            articles = []
            for i, title in enumerate(titles):
                if i > 0:  # Ignorer le premier titre (titre du feed)
                    articles.append({
                        'id': f"rss_{hash(title)}",
                        'title': title.strip(),
                        'releaseDate': datetime.now().timestamp() * 1000
                    })
            
            print(f"✅ {len(articles)} articles récupérés via RSS")
            return articles
        else:
            print(f"❌ Erreur RSS: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur RSS: {e}")
    
    return []

def check_new_articles():
    """Vérifie les nouveaux articles et envoie des alertes"""
    print(f"🚀 Démarrage du monitoring Binance - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Charger les articles déjà vus
    seen_articles = load_seen_articles()
    print(f"📚 {len(seen_articles)} articles déjà vus")
    
    # Récupérer les annonces
    articles = get_binance_announcements()
    
    if not articles:
        print("❌ Aucune annonce récupérée")
        return
    
    print(f"📄 {len(articles)} articles récupérés")
    
    new_articles = []
    
    for article in articles:
        # Créer un ID unique pour l'article
        article_id = str(article.get('id', f"unknown_{hash(article.get('title', ''))}"))
        title = article.get('title', '').lower()
        
        # Vérifier si c'est un nouveau launchpool ou hodler
        is_launchpool = 'binance launchpool' in title
        is_hodler = 'binance hodler' in title
        
        if (is_launchpool or is_hodler) and article_id not in seen_articles:
            new_articles.append(article)
            seen_articles.add(article_id)
            
            # Préparer le message d'alerte
            alert_type = "🚀 NOUVEAU LAUNCHPOOL" if is_launchpool else "💎 NOUVEAU HODLER AIRDROP"
            message = f"{alert_type} DÉTECTÉ!\n\n📢 {article.get('title', 'Titre non disponible')}\n\n🔗 https://www.binance.com/en/support/announcement/list/48\n\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Envoyer l'alerte
            send_telegram_alert(message)
            
            print(f"🎯 Nouvel article détecté: {article.get('title', 'Sans titre')}")
    
    # Sauvegarder les articles vus
    save_seen_articles(seen_articles)
    
    if new_articles:
        print(f"✅ {len(new_articles)} nouveau(x) article(s) détecté(s) et alerté(s)")
    else:
        print("ℹ️ Aucun nouvel article launchpool/hodler détecté")
    
    print("=" * 50)

if __name__ == "__main__":
    try:
        check_new_articles()
    except KeyboardInterrupt:
        print("\n👋 Arrêt du script")
    except Exception as e:
        print(f"❌ Erreur critique: {e}")