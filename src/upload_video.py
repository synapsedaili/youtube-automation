# src/upload_video.py 
import os
import pickle
import base64
import logging
from googleapiclient.discovery import build
from src.config import Config
from src.utils import setup_logging, save_upload_log

logger = setup_logging()

def authenticate_youtube():
    """YouTube API için yetkilendirme yap (SADECE TOKEN İLE)"""
    logger.info("🔑 YouTube API yetkilendirmesi yapılıyor...")
    
    # Token'ı GitHub Secrets'ten al
    encoded_token = os.environ.get("YOUTUBE_TOKEN_ENCODED")
    if not encoded_token:
        raise ValueError("YOUTUBE_TOKEN_ENCODED secret'i ayarlanmamış!")
    
    try:
        # Token'ı decode et
        decoded_token = base64.b64decode(encoded_token)
        
        # Token'ı geçici dosyaya kaydet
        token_path = Config.TEMP_DIR / "token.pickle"
        with open(token_path, "wb") as f:
            f.write(decoded_token)
        
        # Token'ı yükle
        with open(token_path, "rb") as token:
            creds = pickle.load(token)
        
        # Yetkilendirme kontrolü
        if not creds.valid:
            raise ValueError("Token geçersiz veya süresi dolmuş!")
        
        logger.info("✅ YouTube yetkilendirmesi başarılı.")
        return build("youtube", "v3", credentials=creds)
        
    except Exception as e:
        logger.critical(f"❌ YouTube yetkilendirme HATASI: {str(e)}")
        logger.critical("💡 ÇÖZÜM: YENİ TOKEN OLUŞTURUN")
        logger.critical("1. PyCharm'da token_olustur.py çalıştırın")
        logger.critical("2. Çıkan BASE64 token'ı kopyalayın")
        logger.critical("3. GitHub Secrets'te YOUTUBE_TOKEN_ENCODED güncelleyin")
        raise

def upload_to_youtube(video_path: str, title: str, description: str, privacy_status: str, mode: str):
    """Videoyu YouTube'a yükle"""
    youtube = authenticate_youtube()
    
    # YouTube meta verileri
    safe_title = title[:95] + "..." if len(title) > 95 else title
    tags = ["ColdWar", "History", "Shorts", "SynapseDaily"] if mode == "shorts" else ["ColdWarTech", "UnbuiltCities", "RetroFuturism", "HistoryPodcast"]
    category_id = "22" if mode == "shorts" else "27"
    
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
    
    logger.info(f"📤 {mode.upper()} videosu YouTube'a yükleniyor: {safe_title}")
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
    
    # Log kaydet
    save_upload_log(video_id, safe_title, mode)
    
    return video_id
