#!/usr/bin/env python3
"""
Script de surveillance des annonces Binance - Version Scraping Direct
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
        # Configuration Telegram
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
    """Récupère les annonces Binance par scraping direct de la page"""
    try:
        url = "https://www.binance.com/en/support/announcement/list/48"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        print(f"🔍 Scraping direct de la page: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Erreur HTTP: {response.status_code}")
            return []
        
        content = response.text
        print(f"✅ Page récupérée ({len(content)} caractères)")
        
        # Parser le HTML pour extraire les articles
        articles = []
        
        # Méthode 1: Chercher les liens avec les titres
        # Pattern pour les liens d'annonces
        link_pattern = r'<a[^>]*href="([^"]*announcement[^"]*)"[^>]*>([^<]*)</a>'
        matches = re.findall(link_pattern, content, re.IGNORECASE)
        
        for href, title in matches:
            if title.strip():  # Ignorer les liens vides
                articles.append({
                    'id': f"scrape_{hash(title.strip())}",
                    'title': title.strip(),
                    'href': href,
                    'releaseDate': datetime.now().timestamp() * 1000
                })
        
        # Méthode 2: Chercher dans le contenu JavaScript/JSON
        if not articles:
            print("🔄 Recherche dans les données JavaScript...")
            
            # Patterns pour extraire les données des scripts
            json_patterns = [
                r'window\.__APP_DATA\s*=\s*({.*?});',
                r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
                r'"articles"\s*:\s*\[([^\]]*)\]',
                r'"title"\s*:\s*"([^"]*)"'
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, content, re.DOTALL)
                if matches:
                    print(f"✅ Trouvé {len(matches)} correspondances avec pattern")
                    for match in matches:
                        # Essayer d'extraire des titres
                        if isinstance(match, str) and len(match) > 10:
                            title_matches = re.findall(r'"title"\s*:\s*"([^"]*)"', match)
                            for title in title_matches:
                                if title.strip():
                                    articles.append({
                                        'id': f"json_{hash(title.strip())}",
                                        'title': title.strip(),
                                        'releaseDate': datetime.now().timestamp() * 1000
                                    })
                    break
        
        # Méthode 3: Recherche de patterns de titres spécifiques
        if not articles:
            print("🔄 Recherche de patterns spécifiques...")
            
            # Patterns pour les titres contenant launchpool ou hodler
            specific_patterns = [
                r'([^<>]*launchpool[^<>]*)',
                r'([^<>]*hodler[^<>]*)',
                r'([^<>]*Launchpool[^<>]*)',
                r'([^<>]*Hodler[^<>]*)'
            ]
            
            for pattern in specific_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    clean_title = re.sub(r'["\',]', '', match.strip())
                    if len(clean_title) > 10 and clean_title not in [a['title'] for a in articles]:
                        articles.append({
                            'id': f"pattern_{hash(clean_title)}",
                            'title': clean_title,
                            'releaseDate': datetime.now().timestamp() * 1000
                        })
        
        # Nettoyer les doublons
        seen_titles = set()
        unique_articles = []
        for article in articles:
            title_lower = article['title'].lower()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_articles.append(article)
        
        print(f"✅ {len(unique_articles)} articles uniques extraits")
        
        # Afficher les titres trouvés pour debug
        if unique_articles:
            print("📋 Titres extraits:")
            for article in unique_articles[:5]:  # Afficher les 5 premiers
                print(f"  - {article['title']}")
        
        return unique_articles
        
    except Exception as e:
        print(f"❌ Erreur lors du scraping: {e}")
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