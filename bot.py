import tweepy
from curl_cffi import requests
from bs4 import BeautifulSoup
import os
import time

# --- 1. AYARLAR ---
HEDEF_URL = "https://www.hltv.org/results"

# --- 2. GITHUB SIFRELERI (Bu modda kullanilmasa da hata vermemesi icin dursun) ---
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

# --- 4. AKILLI DATA CEKME ---
def ajan_modu():
    print("📢 DENEME MODU: Twitter API kapalı, sadece veri çekilecek...")
    print("HLTV sitesine baglaniliyor...")
    
    try:
        # En guclu yontemle siteye git
        response = requests.get(HEDEF_URL, impersonate="chrome110", timeout=20)
        
        if response.status_code != 200:
            print(f"❌ HATA! Siteye girilemedi. Kod: {response.status_code}")
            return

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # En ustteki maci al
        tum_sonuclar = soup.find_all('div', class_='result-con')
        
        if len(tum_sonuclar) > 0:
            son_mac = tum_sonuclar[0] 
            
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
            
            # --- SIMULASYON CIKTISI ---
            print("\n" + "="*40)
            print("✅ BAŞARILI! Veri çekildi.")
            print("Eğer API açık olsaydı şu tweet atılacaktı:")
            print("-" * 30)
            print(tweet_metni)
            print("-" * 30)
            print("="*40 + "\n")
            
        else:
            print("⚠️ Geçerli bir maç sonucu bulunamadı (Sayfa boş olabilir).")

    except Exception as e:
        print(f"❌ Kritik Hata: {e}")

if __name__ == "__main__":
    ajan_modu()
