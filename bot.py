import tweepy
import cloudscraper # YENI: Engel asici kutuphane
from bs4 import BeautifulSoup
import os
from PIL import Image, ImageDraw, ImageFont

# --- 1. AYARLAR ---
# Test icin genel sonuclar sayfasina bakiyoruz.
# Turnuva ozelinde bakmak istersen burayi degistirebiliriz.
HEDEF_URL = "https://www.hltv.org/results" 
# BURAYI DEGISTIR
TURNUVA_ID = "8240"  # Linkten bulduğun sayıyı buraya yapıştır

# --- 2. GITHUB SIFRELERI ---
api_key = os.environ.get("API_KEY")
api_secret = os.environ.get("API_SECRET")
access_token = os.environ.get("ACCESS_TOKEN")
access_secret = os.environ.get("ACCESS_SECRET")

# --- 3. TWITTER BAGLANTILARI ---
def twitter_auth_v1():
    auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
    return tweepy.API(auth)

def twitter_client_v2():
    return tweepy.Client(consumer_key=api_key, consumer_secret=api_secret, access_token=access_token, access_token_secret=access_secret)

# --- 4. RESIM OLUSTURMA ---
def resim_olustur(takim1, takim2, skor):
    img = Image.new('RGB', (800, 450), color=(15, 20, 30))
    draw = ImageDraw.Draw(img)
    
    # Font ayarlari
    font_buyuk = ImageFont.load_default()
    
    # Baslik
    draw.text((400, 50), "MAC SONUCU", fill=(255, 165, 0), anchor="mm")
    
    # Takimlar ve Skor
    draw.text((200, 225), takim1, fill="white", anchor="mm")
    draw.text((400, 225), skor, fill=(0, 255, 0), anchor="mm")
    draw.text((600, 225), takim2, fill="white", anchor="mm")
    
    img.save("mac_karti.png")
    return "mac_karti.png"

# --- 5. DATA CEKME VE PAYLASMA ---
def siteyi_tara():
    print("HLTV'ye Cloudscraper ile baglaniliyor...")
    
    # Engel asici motoru calistiriyoruz
    scraper = cloudscraper.create_scraper()
    
    try:
        response = scraper.get(HEDEF_URL)
        
        # Eger site hala engelliyorsa kodu gosterelim
        if response.status_code != 200:
            print(f"HATA! Site yine engelledi veya ulasilamadi. Hata Kodu: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # En son maci bul
        son_mac = soup.find('div', class_='result-con')
        
        if son_mac:
            takimlar = son_mac.find_all('div', class_='team')
            takim1 = takimlar[0].text.strip()
            takim2 = takimlar[1].text.strip()
            skor = son_mac.find('td', class_='result-score').text.strip()
            
            print(f"BUNU TWEET ATIYORUM: {takim1} vs {takim2}")
            
            # Gorsel Hazirla
            resim_yolu = resim_olustur(takim1, takim2, skor)
            
            # Twitter'a Yukle
            api_v1 = twitter_auth_v1()
            medya = api_v1.media_upload(resim_yolu)
            
            # Paylas
            client_v2 = twitter_client_v2()
            client_v2.create_tweet(text=f"🔥 Anlık Maç Sonucu:\n\n{takim1} vs {takim2}\nSkor: {skor}\n\n#CS2 #HLTV", media_ids=[medya.media_id])
            print("BASARILI! Tweet atildi.")
            
        else:
            print("Mac sonucu bulunamadi (HTML yapisi farkli olabilir).")

    except Exception as e:
        print(f"Kritik Hata: {e}")

if __name__ == "__main__":
    siteyi_tara()
