import tweepy
from curl_cffi import requests
from bs4 import BeautifulSoup
import os
import time

# --- 1. AYARLAR ---
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

# --- 4. AKILLI DATA CEKME ---
def ajan_modu():
    print("HLTV kontrol ediliyor (Saat kontrolu kapali)...")
    
    try:
        response = requests.get(HEDEF_URL, impersonate="chrome110", timeout=20)
        
        if response.status_code != 200:
            print(f"HATA! Siteye girilemedi. Kod: {response.status_code}")
            return

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Direkt ilk sonucu aliyoruz, saat aramiyoruz.
        tum_sonuclar = soup.find_all('div', class_='result-con')
        
        if len(tum_sonuclar) > 0:
            son_mac = tum_sonuclar[0] # En ustteki (en son) mac
            
            # Verileri al
            takimlar = son_mac.find_all('div', class_='team')
            takim1 = takimlar[0].text.strip()
            takim2 = takimlar[1].text.strip()
            skor_span = son_mac.find('td', class_='result-score')
            skor = skor_span.text.strip() if skor_span else "Bitti"
            
            try:
                turnuva = son_mac.find_parent('div', class_='results-sublist').find('span', class_='event-name').text
            except:
                turnuva = "CS2 Turnuvası"

            print(f"EN SON MAC BULUNDU: {takim1} vs {takim2}")

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
            try:
                client = twitter_client_v2()
                client.create_tweet(text=tweet_metni)
                print("✅ TWEET BASARIYLA ATILDI!")
            
            except tweepy.errors.Forbidden as e:
                # Eger "Duplicate" hatasi gelirse, Twitter "Bunu zaten attin" diyordur.
                if "duplicate" in str(e).lower():
                    print("🛑 DURDURULDU: Bu mac zaten paylasilmis (Twitter engelledi).")
                else:
                    print(f"⚠️ Tweet atilamadi (Yasakli): {e}")
            
            except Exception as e:
                print(f"⚠️ Tweet atarken genel hata: {e}")
            
        else:
            print("Gecerli bir mac sonucu bulunamadi (Sayfa bos veya yapi degismis).")

    except Exception as e:
        print(f"Kritik Hata: {e}")

if __name__ == "__main__":
    ajan_modu()
