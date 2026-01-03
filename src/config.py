# src/config.py
import os
from pathlib import Path

class Config:
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    MODELS_DIR = BASE_DIR / "models"
    TEMP_DIR = BASE_DIR / "temp"
    OUTPUT_DIR = BASE_DIR / "output"
    
    # ✅ EKLENDİ: Dosya yolları
    IDEA_FILE = DATA_DIR / "idea.txt"  # 🟢 Burası eksikti!
    SIDEA_FILE = DATA_DIR / "sidea.txt"  # 🟢 Burası eksikti!
    
    # ✅ EKLENDİ: Karakter limitleri
    SHORTS_CHAR_LIMIT = 1000
    PODCAST_CHAR_LIMIT = 15000
    
    # ✅ EKLENDİ: YouTube ve Hugging Face tokenleri
    HF_TOKEN = os.environ.get("HF_TOKEN", "")
    YOUTUBE_TOKEN_BASE64 = os.environ.get("YOUTUBE_TOKEN_BASE64", "")
    
    # ✅ EKLENDİ: Süreler
    SHORTS_DURATION = 60  # saniye
    PODCAST_DURATION = 900  # saniye (15 dakika)
    
    # ✅ EKLENDİ: Etiketler
    SHORTS_TAGS = ["ColdWar", "History", "Shorts", "SynapseDaily", "RetroFuturism"]
    PODCAST_TAGS = ["ColdWarTech", "UnbuiltCities", "RetroFuturism", "HistoryPodcast", "SynapseDaily"]
    
    @classmethod
    def ensure_directories(cls):
        for dir_path in [cls.MODELS_DIR, cls.TEMP_DIR, cls.OUTPUT_DIR]:
            dir_path.mkdir(exist_ok=True, parents=True)
