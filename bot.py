import tweepy
from curl_cffi import requests # EN GUCLU ENGEL ASICI
from bs4 import BeautifulSoup
import os
import time

# --- 1. AYARLAR ---
# Hem RSS hem Chrome taklidi kullaniyoruz
HEDEF_URL = "https://www.hltv.org/rss/results"

# --- 2. GITHUB SIFRELERI ---
api_key = os.environ.get("API_KEY")
api_secret = os.environ.get("API_SECRET")
access_token = os.environ.get("ACCESS_TOKEN")
access_secret = os.environ.get("ACCESS_SECRET")

# --- 3. TAKIM VE BAYRAK LISTESI ---
TAKIM_BAYRAKLARI = {
    "Eternal Fire": "🇹🇷", "Natus Vincere": "🇺🇦", "NAVI": "🇺🇦",
    "G2": "🇪🇺", "FaZe": "🇪🇺", "Vitality": "🇫🇷", "Spirit": "🇷🇺",
    "MOUZ": "🇪🇺", "Astralis": "🇩🇰", "Liquid": "🇺🇸", "FURIA": "🇧🇷",
    "BIG": "🇩🇪", "Cloud9": "🇺🇸", "Heroic": "🇩🇰", "Virtus.pro": "🇷🇺",
    "Complexity": "🇺🇸", "NiP": "🇸🇪", "ENCE": "🇵🇱", "Falcons": "🇸🇦",
    "The MongolZ": "🇲🇳", "Sangal": "🇪🇺", "B8": "🇺🇦", "Fnatic": "🇪🇺",
    "BetBoom": "🇷🇺", "MIBR": "🇧🇷", "Imperial": "🇧🇷", "paiN": "🇧🇷",
    "SAW": "🇵🇹", "GamerLegion": "🇪🇺", "Apeks": "🇪🇺", "Monte": "🇺🇦",
    "OG": "🇪🇺", "BLEED": "🇪🇺", "3DMAX": "🇫🇷", "FORZE": "🇷🇺",
    "Aurora": "🇷🇺", "Nemiga": "🇷🇺", "SINNERS": "🇨🇿", "KOI": "🇪🇺",
    "PARIVISION": "🇷🇺", "Brave": "🇹🇷", "Wildcard": "🇺🇸"
}

def bayrak_getir(takim_adi):
    for kayitli_takim, bayrak in TAKIM_BAYRAKLARI.items():
        if kayitli_takim.lower() in takim_adi.lower():
            return bayrak
    return ""

def twitter_client_v2():
    return tweepy.Client(consumer_key=api_key, consumer_secret=api_secret, access_token=access_token, access_token_secret=access_secret)

# --- 4. DATA CEKME ---
def ajan_modu():
    print("HLTV 'Chrome 110' Parmak Izi ile kontrol ediliyor...")
    
    try:
        # SIHIRLI KISIM: impersonate="chrome110"
        # Bu satir Cloudflare'e "Yemin ederim ben Chrome tarayicisiyim" der.
        response = requests.get(HEDEF_URL, impersonate="chrome110", timeout=15)
        
        if response.status_code != 200:
            print(f"HATA! Site yine de engelledi. Kod: {response.status_code}")
            return

        # XML verisini parcala
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
        if len(items) > 0:
            son_mac = items[0]
            baslik = son_mac.title.text
            link = son_mac.link.text
            
            if " vs " in baslik:
                parts = baslik.split(" vs ")
                takim1 = parts[0].strip()
                takim2 = parts[1].strip()
            else:
                takim1 = "Takım A"
                takim2 = "Takım B"
            
            print(f"VERI ALINDI: {baslik}")

            # Hafiza Kontrolu
            client = twitter_client_v2()
            try:
                me = client.get_me()
                tweets = client.get_users_tweets(id=me.data.id, max_results=5)
                if tweets.data:
                    for tweet in tweets.data:
                        if takim1 in tweet.text and takim2 in tweet.text:
                            print(f"🛑 ZATEN PAYLASILMIS: {baslik}")
                            return
            except Exception as e:
                print(f"Hafiza hatasi (onemsiz): {e}")

            # Tweet Hazirla
            bayrak1 = bayrak_getir(takim1)
            bayrak2 = bayrak_getir(takim2)
            
            tweet_metni = (
                f"🚨 MAÇ SONUCU\n\n"
                f"{takim1} {bayrak1} 🆚 {takim2} {bayrak2}\n\n"
                f"Link: {link}\n"
                f"#CS2 #HLTV"
            )
            
            # --- TWEET AT ---
            client.create_tweet(text=tweet_metni)
            print("✅ TWEET BASARIYLA ATILDI (Curl_CFFI Yontemi)")
            
        else:
            print("RSS Listesi bos.")

    except Exception as e:
        print(f"Kritik Hata: {e}")

if __name__ == "__main__":
    ajan_modu()
