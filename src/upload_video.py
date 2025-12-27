# src/upload_video.py
import os
import pickle
import logging
from pathlib import Path
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from src.config import Config
from src.utils import setup_logging, decode_youtube_credentials

logger = setup_logging()

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def authenticate_youtube():
    """YouTube API için yetkilendirme yap."""
    logger.info("🔑 YouTube API yetkilendirmesi yapılıyor...")
    
    # client_secret.json'ı decode et
    client_secret_path = decode_youtube_credentials()
    
    # token.pickle dosyasını GitHub Secrets'ten al (varsa)
    token_pickle_b64 = os.environ.get("YOUTUBE_TOKEN_PICKLE")
    if token_pickle_b64:
        import base64
        token_data = base64.b64decode(token_pickle_b64)
        token_path = Config.TEMP_DIR / "token.pickle"
        with open(token_path, "wb") as f:
            f.write(token_data)
        
        # token.pickle dosyasını yükle
        creds = None
        if token_path.exists():
            with open(token_path, "rb") as token:
                creds = pickle.load(token)
        
        # Yetkilendirme
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        
        logger.info("✅ GitHub Secrets'ten token.pickle kullanıldı.")
        return build("youtube", "v3", credentials=creds)
    else:
        # token.pickle yoksa OAuth2 başlat (bu GitHub Actions'ta çalışmaz!)
        logger.error("❌ token.pickle GitHub Secrets'te bulunamadı!")
        logger.error("⚠️ Lütfen PyCharm'da oluşturduğunuz token.pickle dosyasını GitHub Secrets'e ekleyin.")
        raise ValueError("token.pickle eksik!")
