import tweepy
from curl_cffi import requests
from bs4 import BeautifulSoup
import os
import time

# --- 1. AYARLAR ---
HEDEF_URL = "https://www.hltv.org/results"
# 20 dakika ayari cok onemli! 
# Bot 15 dk'da bir calisir. Eger mac 20 dk'dan eskiyse "Bunu zaten gormusumdur" der ve atlar.
MAX_DAKIKA = 20 

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
    print(f"HLTV kontrol ediliyor (Sadece son {MAX_DAKIKA} dakikadaki maclar)...")
    
    try:
        # Chrome taklidi ile siteye gir
        response = requests.get(HEDEF_URL, impersonate="chrome110", timeout=20)
        
        if response.status_code != 200:
            print(f"HATA! Siteye girilemedi. Kod: {response.status_code}")
            return

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Tum sonuclari al
        tum_sonuclar = soup.find_all('div', class_='result-con')
        son_mac = None
        
        # Listeyi tara ve zamani okunabilen ilk gecerli maci bul
        for aday in tum_sonuclar:
            if 'data-unix' in aday.attrs:
                son_mac = aday
                break 
        
        if son_mac:
            # --- BEDAVA HAFIZA (ZAMAN KONTROLU) ---
            try:
                mac_zamani_ms = int(son_mac['data-unix'])
                mac_zamani_sec = mac_zamani_ms / 1000
                su_an = time.time()
                gecen_sure_dk = (su_an - mac_zamani_sec) / 60
                
                print(f"Tespit edilen maç {int(gecen_sure_dk)} dakika önce bitmiş.")
                
                # Eger mac 20 dakikadan eskiyse PAYLASMA.
                # Cunku bot 15 dk'da bir calisiyor, demek ki bunu onceki turda paylasti.
                if gecen_sure_dk > MAX_DAKIKA:
                    print(f"🛑 ESKI MAC TESPIT EDILDI ({int(gecen_sure_dk)} dk). Pas geciliyor.")
                    return 
                    
            except Exception as e:
                print(f"Zaman okunamadi, risk almamak icin paylasilmiyor: {e}")
                return

            # Eger buraya geldiysek mac tazedir (0-20 dk arasi).
            takimlar = son_mac.find_all('div', class_='team')
            takim1 = takimlar[0].text.strip()
            takim2 = takimlar[1].text.strip()
            skor_span = son_mac.find('td', class_='result-score')
            skor = skor_span.text.strip() if skor_span else "Bitti"
            
            try:
                turnuva = son_mac.find_parent('div', class_='results-sublist').find('span', class_='event-name').text
            except:
                turnuva = "CS2 Turnuvası"

            print(f"✅ YENI MAC! TWEET HAZIRLANIYOR: {takim1} vs {takim2}")

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
                # Eger cok sanssizsak ve Twitter "Duplicate" derse:
                if "duplicate" in str(e).lower():
                    print("🛑 Twitter engelledi: Bu tweet zaten var.")
                else:
                    print(f"⚠️ HATA: {e}")
            
        else:
            print("Gecerli mac bulunamadi.")

    except Exception as e:
        print(f"Kritik Hata: {e}")

if __name__ == "__main__":
    ajan_modu()
