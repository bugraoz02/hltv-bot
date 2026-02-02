import tweepy
import cloudscraper
from bs4 import BeautifulSoup
import os
import time
import random

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
    "PARIVISION": "🇷🇺", "Brave": "🇹🇷"
}

def bayrak_getir(takim_adi):
    for kayitli_takim, bayrak in TAKIM_BAYRAKLARI.items():
        if kayitli_takim.lower() in takim_adi.lower():
            return bayrak
    return ""

def twitter_client_v2():
    return tweepy.Client(consumer_key=api_key, consumer_secret=api_secret, access_token=access_token, access_token_secret=access_secret)

# --- 4. DATA CEKME ---
def siteyi_tara():
    print("HLTV Guclendirilmis Mod ile kontrol ediliyor...")
    
    # --- YENILIK: Gercek Masaustu Tarayicisi Taklidi ---
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    # Twitter istemcisi (Hafiza kontrolu icin)
    client = twitter_client_v2()
    
    try:
        # Sonuc sayfasini cek
        response = scraper.get(HEDEF_URL)
        
        if response.status_code != 200:
            print(f"HATA! Engel asilamadi. Kod: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        son_mac = soup.find('div', class_='result-con')
        
        if son_mac:
            # Temel Bilgiler
            takimlar = son_mac.find_all('div', class_='team')
            takim1_isim = takimlar[0].text.strip()
            takim2_isim = takimlar[1].text.strip()
            skor = son_mac.find('td', class_='result-score').text.strip()
            
            # Hafiza Kontrolu (Daha once paylasildi mi?)
            try:
                me = client.get_me()
                my_id = me.data.id
                tweets = client.get_users_tweets(id=my_id, max_results=5)
                zaten_var = False
                if tweets.data:
                    for tweet in tweets.data:
                        if takim1_isim in tweet.text and takim2_isim in tweet.text:
                            zaten_var = True
                            break
                
                if zaten_var:
                    print(f"DURDURULDU: {takim1_isim} vs {takim2_isim} zaten paylasilmis.")
                    return
            except:
                pass # Hafiza hatasi olursa devam et

            # Turnuva Adi
            try:
                turnuva = son_mac.find_parent('div', class_='results-sublist').find('span', class_='event-name').text
            except:
                turnuva = "CS2 Turnuvası"

            # --- MVP BULMA (HATA VERIRSE GEC) ---
            mvp_bilgisi = "Seçilmedi"
            try:
                mac_linki = son_mac.find('a', class_='a-reset')['href']
                tam_link = "https://www.hltv.org" + mac_linki
                
                # Sitede cok hizli gezince blok yiyoruz, biraz bekle
                time.sleep(random.uniform(1, 3))
                
                mac_response = scraper.get(tam_link)
                if mac_response.status_code == 200:
                    mac_soup = BeautifulSoup(mac_response.text, 'html.parser')
                    mvp_kutusu = mac_soup.find('div', class_='highlighted-player')
                    if mvp_kutusu:
                        oyuncu_adi = mvp_kutusu.find('span', class_='player-nick').text.strip()
                        stats = mvp_kutusu.find('div', class_='stats')
                        rating = stats.find('span', class_='value').text.strip() if stats else ""
                        mvp_bilgisi = f"{oyuncu_adi} ({rating} Rating)"
                else:
                    print("MVP detayina girilemedi (Engel).")
            except:
                mvp_bilgisi = "Veri Yok"

            # --- TWEET HAZIRLA ---
            bayrak1 = bayrak_getir(takim1_isim)
            bayrak2 = bayrak_getir(takim2_isim)
            
            tweet_metni = (
                f"{takim1_isim} {bayrak1} vs {takim2_isim} {bayrak2}\n"
                f"Skor: {skor}\n\n"
                f"🌟 Maçın Oyuncusu: {mvp_bilgisi}\n\n"
                f"🏆 {turnuva}\n"
                f"#CS2"
            )
            
            print("\n" + "="*40)
            print("BASARILI! ENGEL ASILDI. TWEET HAZIR:")
            print("-" * 20)
            print(tweet_metni)
            print("-" * 20)
            
            # --- TWEET ATMAK ICIN ASAGIDAKI SATIRIN BASINDAKI # ISARETINI SIL ---
            # client.create_tweet(text=tweet_metni) 
            # print("✅ TWEET GONDERILDI")
            
        else:
            print("Mac sonucu bulunamadi.")

    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    siteyi_tara()
