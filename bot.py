import tweepy
import requests # RSS icin cloudscraper yerine requests yeterli olabilir
from bs4 import BeautifulSoup
import os
import time

# --- 1. AYARLAR ---
# ARTIK HTML DEGIL, RSS FEED KULLANIYORUZ (ARKA KAPI)
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

# --- 4. RSS DATA CEKME ---
def rss_tara():
    print("HLTV RSS Feed (Arka Kapi) kontrol ediliyor...")
    
    # RSS okurken Google Bot taklidi yapiyoruz, genelde izin verirler
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
    }
    
    try:
        response = requests.get(HEDEF_URL, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"HATA! RSS Kapisi da kapali. Kod: {response.status_code}")
            return

        # XML verisini parcala
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
        if len(items) > 0:
            son_mac = items[0] # En ustteki (en son) mac
            
            # Baslik: "Team A vs Team B" formatindadir
            baslik = son_mac.title.text
            link = son_mac.link.text
            aciklama = son_mac.description.text 
            
            # Takimlari ayikla (Genelde ' vs ' ile ayrilir)
            if " vs " in baslik:
                parts = baslik.split(" vs ")
                takim1 = parts[0].strip()
                takim2 = parts[1].strip()
            else:
                takim1 = "Takım A"
                takim2 = "Takım B"
            
            print(f"RSS Verisi Cekildi: {baslik}")

            # Hafiza Kontrolu
            client = twitter_client_v2()
            try:
                me = client.get_me()
                tweets = client.get_users_tweets(id=me.data.id, max_results=5)
                if tweets.data:
                    for tweet in tweets.data:
                        # RSS basliklari cok nettir, direkt kiyaslayabiliriz
                        if takim1 in tweet.text and takim2 in tweet.text:
                            print(f"🛑 ZATEN PAYLASILMIS: {baslik}")
                            return
            except:
                pass

            # Tweet Hazirla
            bayrak1 = bayrak_getir(takim1)
            bayrak2 = bayrak_getir(takim2)
            
            # RSS'de skor bazen aciklamada yazar, bazen yazmaz.
            # Garanti olsun diye baslik ve linki paylasiyoruz.
            
            tweet_metni = (
                f"🚨 MAÇ SONUCU\n\n"
                f"{takim1} {bayrak1} 🆚 {takim2} {bayrak2}\n\n"
                f"Detaylar: {link}\n"
                f"#CS2 #HLTV"
            )
            
            # --- TWEET AT ---
            print("TWEET GONDERILIYOR...")
            client.create_tweet(text=tweet_metni)
            print("✅ TWEET BASARIYLA ATILDI (RSS Yontemi)")
            
        else:
            print("RSS Listesi bos.")

    except Exception as e:
        print(f"RSS Hatasi: {e}")

if __name__ == "__main__":
    rss_tara()
