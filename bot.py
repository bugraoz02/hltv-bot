import tweepy
import requests
from bs4 import BeautifulSoup
import os
from PIL import Image, ImageDraw, ImageFont

# --- 1. AYARLAR ---
# BURAYI DEGISTIR: Takip etmek istedigin turnuvanin ID'si
# Ornek: hltv.org/events/7438/iem-katowice (Buradaki 7438 ID'dir)
TURNUVA_ID = "8240" 

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
def resim_olustur(takim1, takim2, skor, asama, turnuva_adi):
    # Arka plan (Siyah/Lacivert)
    img = Image.new('RGB', (800, 450), color=(15, 20, 30))
    draw = ImageDraw.Draw(img)
    
    # Font ayarlari (Varsayilan fontu kullanir)
    font_buyuk = ImageFont.load_default()
    font_orta = ImageFont.load_default()
    
    # Baslik
    baslik = f"{turnuva_adi} | {asama}"
    draw.text((400, 50), baslik, fill=(255, 200, 0), anchor="mm")

    # Takim 1
    draw.text((200, 225), takim1, fill="white", anchor="mm")

    # Skor (Buyuk)
    draw.text((400, 225), skor, fill=(0, 255, 100), anchor="mm")

    # Takim 2
    draw.text((600, 225), takim2, fill="white", anchor="mm")

    # Alt Bilgi
    draw.text((400, 400), "MAC SONUCU", fill=(100, 100, 150), anchor="mm")
    
    img.save("turnuva_karti.png")
    return "turnuva_karti.png"

# --- 5. DATA CEKME VE PAYLASMA ---
def turnuva_takip_et():
    # Sadece secilen turnuvanin sonuclarina gidiyoruz
    url = f"https://www.hltv.org/results?event={TURNUVA_ID}"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        print(f"{TURNUVA_ID} nolu turnuva kontrol ediliyor...")
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print("Siteye ulasilamadi.")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Turnuva adini al
        turnuva_baslik = soup.find('div', class_='event-name')
        turnuva_adi = turnuva_baslik.text.strip() if turnuva_baslik else "Turnuva"

        # En son biten maci bul
        son_sonuc = soup.find('div', class_='result-con')
        
        if son_sonuc:
            takimlar = son_sonuc.find_all('div', class_='team')
            takim1 = takimlar[0].text.strip()
            takim2 = takimlar[1].text.strip()
            skor = son_sonuc.find('td', class_='result-score').text.strip()
            
            # Asama bilgisi (Orn: Semi-final)
            try:
                # Event texti genelde result-con icinde veya ustunde olur
                asama = son_sonuc.find_parent('div', class_='results-sublist').find('span', class_='event-name').text
            except:
                asama = "Match Day"

            print(f"Mac Bulundu: {takim1} vs {takim2} - {skor}")

            # 1. Gorseli Olustur
            resim = resim_olustur(takim1, takim2, skor, asama, turnuva_adi)
            
            # 2. Twitter'a Yukle
            api_v1 = twitter_auth_v1()
            medya = api_v1.media_upload(resim)
            
            # 3. Paylas
            tweet_metni = f"🏆 {turnuva_adi}\n\n⚔️ {takim1} vs {takim2}\n📊 Skor: {skor}\n\nKazanan taraf belli oldu! #CS2 #Esports"
            
            client_v2 = twitter_client_v2()
            client_v2.create_tweet(text=tweet_metni, media_ids=[medya.media_id])
            print("Tweet atildi!")
            
        else:
            print("Bu turnuvada henuz sonuc yok veya maclar baslamadi.")

    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    turnuva_takip_et()
