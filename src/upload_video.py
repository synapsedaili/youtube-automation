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
    client_secret = decode_youtube_credentials()
    token_path = Config.TEMP_DIR / "token.pickle"
    creds = None
    if token_path.exists():
        with open(token_path, "rb") as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret, SCOPES)
            creds = flow.run_local_server(port=0, open_browser=False)
        with open(token_path, "wb") as f:
            pickle.dump(creds, f)
    return build("youtube", "v3", credentials=creds)

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
