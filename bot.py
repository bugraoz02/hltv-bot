import tweepy
from curl_cffi import requests # EN GUCLU SILAH
from bs4 import BeautifulSoup
import os
import time

# --- 1. AYARLAR ---
# RSS (404) bitti, tekrar ana siteye donuyoruz
HEDEF_URL = "https://www.hltv.org/results"

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
    print("HLTV Ana Sayfasi 'Chrome 110' ile zorlaniyor...")
    
    try:
        # Ana siteye en guclu taklitle giriyoruz
        response = requests.get(HEDEF_URL, impersonate="chrome110", timeout=20)
        
        # Eger yine engellerse kodu gorelim
        if response.status_code != 200:
            print(f"HATA! Erişim Engellendi. Kod: {response.status_code}")
            return

        soup = BeautifulSoup(response.content, 'html.parser')
        son_mac = soup.find('div', class_='result-con')
        
        if son_mac:
            # HTML yapisindan verileri al
            takimlar = son_mac.find_all('div', class_='team')
            takim1 = takimlar[0].text.strip()
            takim2 = takimlar[1].text.strip()
            skor_span = son_mac.find('td', class_='result-score')
            skor = skor_span.text.strip() if skor_span else "Bitti"
            
            # Turnuva adi
            try:
                turnuva = son_mac.find_parent('div', class_='results-sublist').find('span', class_='event-name').text
            except:
                turnuva = "CS2 Turnuvası"

            print(f"VERI ALINDI: {takim1} vs {takim2}")

            # Hafiza Kontrolu
            client = twitter_client_v2()
            try:
                me = client.get_me()
                tweets = client.get_users_tweets(id=me.data.id, max_results=5)
                if tweets.data:
                    for tweet in tweets.data:
                        if takim1 in tweet.text and takim2 in tweet.text:
                            print(f"🛑 ZATEN PAYLASILMIS: {takim1} vs {takim2}")
                            return
            except Exception as e:
                print(f"Hafiza hatasi (onemsiz): {e}")

            # Tweet Hazirla
            bayrak1 = bayrak_getir(takim1)
            bayrak2 = bayrak_getir(takim2)
            
            tweet_metni = (
                f"🚨 MAÇ SONUCU\n\n"
                f"{takim1} {bayrak1} 🆚 {takim2} {bayrak2}\n"
                f"Skor: {skor}\n\n"
                f"🏆 {turnuva}\n"
                f"#CS2 #HLTV"
            )
            
            # --- TWEET AT ---
            client.create_tweet(text=tweet_metni)
            print("✅ TWEET BASARIYLA ATILDI (Curl_CFFI + HTML Yontemi)")
            
        else:
            print("Sayfa acildi ama mac sonucu bulunamadi (HTML yapisi degismis olabilir).")

    except Exception as e:
        print(f"Kritik Hata: {e}")

if __name__ == "__main__":
    ajan_modu()
