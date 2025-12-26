# src/upload_video.py
import os
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1" 
import pickle
import base64
import logging
import json
from pathlib import Path
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from src.config import Config
from src.utils import setup_logging

logger = setup_logging()

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def decode_youtube_credentials():
    """GitHub Secrets'ten YouTube kimlik bilgilerini decode et."""
    logger.info("🔑 YouTube kimlik bilgileri decode ediliyor...")
    
    # Hem eski hem yeni secret isimlerini dene
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
        logger.error(f"Decoded data snippet: {decoded_data[:100]}...")  # Hata ayıklama için
        raise
def authenticate_youtube():
    """YouTube API için yetkilendirme yap."""
    logger.info("🔑 YouTube API yetkilendirmesi yapılıyor...")
    
    # client_secret.json'ı decode et
    client_secret_path = decode_youtube_credentials()
    
    # Token yönetimi
    token_path = Config.TEMP_DIR / "token.pickle"
    creds = None
    
    if token_path.exists():
        with open(token_path, "rb") as token:
            creds = pickle.load(token)
    
    # Yetkilendirme
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secret_path, SCOPES
            )
            creds = flow.run_local_server(port=0, open_browser=False)
        
        # Token'ı kaydet
        with open(token_path, "wb") as token:
            pickle.dump(creds, token)
    
    logger.info("✅ YouTube yetkilendirmesi başarılı.")
    return build("youtube", "v3", credentials=creds)

def upload_to_youtube(video_path: str, title: str, description: str, privacy_status: str, mode: str):
    """Videoyu YouTube'a yükle."""
    youtube = authenticate_youtube()

    # YouTube meta verileri
    safe_title = title[:95] + "..." if len(title) > 95 else title
    tags = Config.SHORTS_TAGS if mode == "shorts" else Config.PODCAST_TAGS
    category_id = "22" if mode == "shorts" else "27"  # People & Blogs / Education

    request_body = {
        "snippet": {
            "title": safe_title,
            "description": description,
            "tags": tags,
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": privacy_status
        }
    }

    # Upload
    logger.info(f"📤 {mode.upper()} videosu YouTube'a yükleniyor: {title}")
    media_file = MediaFileUpload(video_path, chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media_file
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            progress = int(status.progress() * 100)
            logger.info(f"📤 Upload ilerlemesi: %{progress}")

    video_id = response["id"]
    logger.info(f"✅ YouTube ID: {video_id}")
    
    return video_id
