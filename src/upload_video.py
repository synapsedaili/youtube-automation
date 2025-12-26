# src/upload_video.py
import os
import pickle
import base64
import json
import logging
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from src.config import Config
from src.utils import setup_logging
import time
import webbrowser

logger = setup_logging()

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def decode_youtube_credentials():
    """GitHub Secrets'ten YouTube kimlik bilgilerini decode et."""
    logger.info("🔑 YouTube kimlik bilgileri decode ediliyor...")
    
    encoded_credentials = os.environ.get("YOUTUBE_TOKEN_ENCODED") or os.environ.get("YOUTUBE_CREDENTIALS")
    
    if not encoded_credentials:
        raise ValueError("YOUTUBE_CREDENTIALS veya YOUTUBE_TOKEN_ENCODED ayarlanmamış!")
    
    try:
        decoded_data = base64.b64decode(encoded_credentials).decode("utf-8")
        
        try:
            credentials = json.loads(decoded_data)
            is_json = True
        except:
            is_json = False
        
        if is_json:
            client_secret_path = Config.TEMP_DIR / "client_secret.json"
            with open(client_secret_path, "w") as f:
                json.dump(credentials, f)
            logger.info("✅ YouTube kimlik bilgileri (JSON) başarıyla decode edildi.")
            return str(client_secret_path)
        else:
            token_path = Config.TEMP_DIR / "token.pickle"
            with open(token_path, "wb") as f:
                f.write(decoded_data.encode("latin-1") if isinstance(decoded_data, str) else decoded_data)
            logger.info("✅ YouTube token.pickle dosyası başarıyla decode edildi.")
            return str(token_path)
            
    except Exception as e:
        logger.error(f"❌ Kimlik bilgileri decode hatası: {str(e)}")
        logger.error(f"Decoded data snippet: {decoded_data[:100]}...")
        raise

def authenticate_youtube():
    """YouTube API için yetkilendirme yap (detaylı loglama ile)"""
    logger.info("🔑 YouTube API yetkilendirmesi yapılıyor...")
    logger.info("⏳ Bu işlem 1-2 dakika sürebilir. Lütfen bekleyin...")
    
    client_secret_path = decode_youtube_credentials()
    token_path = Config.TEMP_DIR / "token.pickle"
    creds = None
    
    # 1. Token varsa yükle
    if token_path.exists():
        logger.info("🔑 Mevcut token.pickle dosyası yükleniyor...")
        with open(token_path, "rb") as token:
            creds = pickle.load(token)
    
    # 2. Yetkilendirme gerekiyorsa
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("🔄 Token yenileniyor...")
            creds.refresh(Request())
        else:
            logger.info("🌐 Google OAuth akışı başlatılıyor...")
            logger.info("❗ Bu ilk çalıştırmada MANUEL ONAY gerekecek!")
            logger.info("❗ Lütfen logları dikkatle takip edin!")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secret_path, 
                SCOPES,
                redirect_uri='urn:ietf:wg:oauth:2.0:oob'  # Manuel onay için
            )
            
            # OAuth URL'sini oluştur
            auth_url, _ = flow.authorization_url(prompt='consent')
            
            logger.info("\n" + "="*60)
            logger.info("🔐 GOOGLE OAUTH MANUEL ONAY GEREKİR!")
            logger.info("AŞAĞIDAKİ URL'Yİ TARAYICINIZA YAPIŞTIRIN:")
            logger.info(f"\033[1;32m{auth_url}\033[0m")  # Yeşil renkli URL
            logger.info("="*60 + "\n")
            
            # Kullanıcıdan kodu al
            code = input("Google'dan aldığınız kodu buraya yapıştırın: ").strip()
            
            # Token oluştur
            flow.fetch_token(code=code)
            creds = flow.credentials
            
            # Token'ı kaydet
            with open(token_path, "wb") as token:
                pickle.dump(creds, token)
            logger.info("✅ Yeni token.pickle dosyası oluşturuldu!")
    
    logger.info("✅ YouTube yetkilendirmesi başarılı!")
    return build("youtube", "v3", credentials=creds)
