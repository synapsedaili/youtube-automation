# src/upload_video.py
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from src.config import Config
from src.utils import setup_logging, decode_youtube_credentials

logger = setup_logging()
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def authenticate_youtube():
    logger.info("🔑 YouTube API yetkilendirmesi yapılıyor...")
    
    # Önce client_secret.json'ı oluştur
    client_secret_path = decode_youtube_credentials()
    
    # Yeni: GitHub Secrets'ten token.pickle al
    token_pickle_b64 = os.environ.get("YOUTUBE_TOKEN_PICKLE", "")
    token_path = Config.TEMP_DIR / "token.pickle"
    
    if token_pickle_b64:
        # base64'i decode et
        import base64
        token_data = base64.b64decode(token_pickle_b64)
        with open(token_path, "wb") as f:
            f.write(token_data)
        logger.info("✅ token.pickle GitHub Secrets'ten yüklendi.")

def upload_to_youtube(video_path: str, title: str, description: str, privacy_status: str, mode: str):
    youtube = authenticate_youtube()
    safe_title = (title[:95] + "...") if len(title) > 95 else title
    tags = Config.SHORTS_TAGS if mode == "shorts" else Config.PODCAST_TAGS
    category_id = "22" if mode == "shorts" else "27"
    
    body = {
        "snippet": {"title": safe_title, "description": description, "tags": tags, "categoryId": category_id},
        "status": {"privacyStatus": privacy_status}
    }
    
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    
    response = None
    while response is None:
        status, response = request.next_chunk()
    
    logger.info(f"✅ YouTube ID: {response['id']}")
    return response["id"]
