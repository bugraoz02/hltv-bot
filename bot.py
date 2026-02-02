import tweepy
import cloudscraper
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
    "PARIVISION": "🇷🇺", "Brave": "🇹🇷"
}

def bayrak_getir(takim_adi):
    for kayitli_takim, bayrak in TAKIM_BAYRAKLARI.items():
        if kayitli_takim.lower() in takim_adi.lower():
            return bayrak
    return ""

# --- 4. TWITTER BAGLANTILARI ---
def twitter_client_v2():
    return tweepy.Client(consumer_key=api_key, consumer_secret=api_secret, access_token=access_token, access_token_secret=access_secret)

# --- 5. HAFIZA KONTROLU (AYNI MACI PAYLASMAMAK ICIN) ---
def daha_once_paylasildi_mi(client, takim1, takim2):
    try:
        # Senin attigin son 5 tweeti kontrol et
        me = client.get_me()
        my_id = me.data.id
        tweets = client.get_users_tweets(id=my_id, max_results=5)
        
        if not tweets.data:
            return False # Hic tweet yoksa paylasilmamistir

        for tweet in tweets.data:
            # Eger son tweetlerde iki takimin adi da geciyorsa "Paylasildi" say
            if takim1 in tweet.text and takim2 in tweet.text:
                return True
        return False
    except Exception as e:
        print(f"Hafiza kontrolunde hata (Onemsiz): {e}")
        return False

# --- 6. ANA PROGRAM ---
def siteyi_tara():
    print("Bot baslatiliyor...")
    scraper = cloudscraper.create_scraper()
    
    # Twitter baglantisini basta kuralim (Hafiza kontrolu icin lazim)
    client = twitter_client_v2()
    
    try:
        response = scraper.get(HEDEF_URL)
        if response.status_code != 200:
            print("Siteye girilemedi.")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        son_mac = soup.find('div', class_='result-con')
        
        if son_mac:
            # Temel Bilgiler
            takimlar = son_mac.find_all('div', class_='team')
            takim1_isim = takimlar[0].text.strip()
            takim2_isim = takimlar[1].text.strip()
            skor = son_mac.find('td', class_='result-score').text.strip()
            
            # --- KRITIK KONTROL: TEKRAR PAYLASIMI ENGELLEME ---
            if daha_once_paylasildi_mi(client, takim1_isim, takim2_isim):
                print(f"🛑 DURDURULDU: {takim1_isim} vs {takim2_isim} maci zaten paylasilmis.")
                return # Programi burada bitir, tweet atma.

            # Eger paylasilmadiysa devam et...
            try:
                turnuva = son_mac.find_parent('div', class_='results-sublist').find('span', class_='event-name').text
            except:
                turnuva = "CS2 Turnuvası"

            # --- MVP BULMA ---
            mvp_bilgisi = "Seçilmedi"
            try:
                mac_linki = son_mac.find('a', class_='a-reset')['href']
                tam_link = "https://www.hltv.org" + mac_linki
                print(f"Detaylar icin mac sayfasina gidiliyor: {tam_link}")
                
                mac_response = scraper.get(tam_link)
                mac_soup = BeautifulSoup(mac_response.text, 'html.parser')
                
                mvp_kutusu = mac_soup.find('div', class_='highlighted-player')
                if mvp_kutusu:
                    oyuncu_adi = mvp_kutusu.find('span', class_='player-nick').text.strip()
                    stats = mvp_kutusu.find('div', class_='stats')
                    rating = stats.find('span', class_='value').text.strip() if stats else "N/A"
                    mvp_bilgisi = f"{oyuncu_adi} ({rating} Rating)"
            except:
                pass

            # --- TWEET HAZIRLAMA ---
            bayrak1 = bayrak_getir(takim1_isim)
            bayrak2 = bayrak_getir(takim2_isim)
            
            tweet_metni = (
                f"{takim1_isim} {bayrak1} vs {takim2_isim} {bayrak2}\n"
                f"Skor: {skor}\n\n"
                f"🌟 Maçın Oyuncusu: {mvp_bilgisi}\n\n"
                f"🏆 {turnuva}\n"
                f"#CS2"
            )
            
            # --- TEST MODU (LOGLARA YAZAR) ---
            print("\n" + "="*40)
            print("AYNI TWEET BULUNAMADI, PAYLASIMA HAZIR:")
            print("-" * 20)
            print(tweet_metni)
            print("-" * 20)
            
            # --- GERCEK PAYLASIM (AKTIF ETMEK ICIN ALTTAKI '#' ISARETINI SIL) ---
            # client.create_tweet(text=tweet_metni) 
            # print("✅ TWEET BASARIYLA ATILDI!")
            
        else:
            print("Mac sonucu bulunamadi.")

    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    siteyi_tara()
