import tweepy
from curl_cffi import requests
from bs4 import BeautifulSoup
import os
import time

# --- 1. AYARLAR ---
HEDEF_URL = "https://www.hltv.org/results"
MAX_DAKIKA = 25  # Mac biteli 25 dakikayi gectiyse "Eski" say ve paylasma.

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
    print(f"HLTV kontrol ediliyor (Zaman Siniri: {MAX_DAKIKA} dk)...")
    
    try:
        # Chrome 124 taklidi (En guncel tarayici kimligi)
        response = requests.get(HEDEF_URL, impersonate="chrome124", timeout=30)
        
        if response.status_code != 200:
            print(f"HATA! Siteye girilemedi. Kod: {response.status_code}")
            return

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Sonuc kutularini bul
        tum_sonuclar = soup.find_all('div', class_='result-con')
        
        if not tum_sonuclar:
            print("Sayfada mac sonucu bulunamadi.")
            return

        # En ustteki maci al
        son_mac = tum_sonuclar[0]
        
        # --- ZAMAN KONTROL MEKANIZMASI ---
        tweet_atilsin_mi = True
        
        # 'data-unix' etiketi var mi diye kontrol et (.get metodu hata vermez, yoksa None doner)
        unix_zaman = son_mac.get('data-unix')
        
        if unix_zaman:
            try:
                mac_zamani_ms = int(unix_zaman)
                mac_zamani_sec = mac_zamani_ms / 1000
                su_an = time.time()
                gecen_sure_dk = (su_an - mac_zamani_sec) / 60
                
                print(f"🕒 Bu maç {int(gecen_sure_dk)} dakika önce bitmiş.")
                
                if gecen_sure_dk > MAX_DAKIKA:
                    print(f"⛔ ESKI MAC! ({int(gecen_sure_dk)} dk > {MAX_DAKIKA} dk). Paylaşılmayacak.")
                    tweet_atilsin_mi = False
                else:
                    print("✅ MAÇ YENİ! Paylaşıma uygun.")
                    
            except:
                print("⚠️ Zaman etiketi var ama okunamadı. Yinede deneniyor.")
        else:
            print("⚠️ Zaman etiketi bulunamadı (HLTV gizlemiş). Twitter kontrolüne güvenilecek.")

        # Eger zaman kontrolunden gectiyse veya zaman bulunamadiysa devam et
        if tweet_atilsin_mi:
            takimlar = son_mac.find_all('div', class_='team')
            if len(takimlar) >= 2:
                takim1 = takimlar[0].text.strip()
                takim2 = takimlar[1].text.strip()
            else:
                return

            skor_span = son_mac.find('td', class_='result-score')
            skor = skor_span.text.strip() if skor_span else "Bitti"
            
            try:
                turnuva = son_mac.find_parent('div', class_='results-sublist').find('span', class_='event-name').text
            except:
                turnuva = "CS2 Turnuvası"

            print(f"🐦 TWEET HAZIRLANIYOR: {takim1} vs {takim2}")

            tweet_metni = (
                f"🚨 MAÇ SONUCU\n\n"
                f"{takim1} {bayrak1} 🆚 {takim2} {bayrak2}\n"
                f"Skor: {skor}\n\n"
                f"🏆 {turnuva}\n"
                f"#CS2 #HLTV"
            )
            
            # --- TWEET AT ---
            try:
                client = twitter_client_v2()
                client.create_tweet(text=tweet_metni)
                print("✅ TWEET BASARIYLA ATILDI!")
            
            except tweepy.errors.Forbidden as e:
                if "duplicate" in str(e).lower():
                    print("🛑 DURDURULDU: Bu tweet zaten var (Twitter Duplicate Koruması).")
                else:
                    print(f"⚠️ HATA: {e}")
            except Exception as e:
                print(f"Genel Hata: {e}")

    except Exception as e:
        print(f"Kritik Hata: {e}")

if __name__ == "__main__":
    ajan_modu()
