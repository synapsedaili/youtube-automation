# src/tts/tts_manager.py
import os
import logging
import urllib.request
from pathlib import Path
from src.config import Config
from src.utils import setup_logging

logger = setup_logging()

class TTSManager:
    """Limitsiz ses yönetimi sistemi - Piper TTS ile"""
    
    def __init__(self):
        self.podcast_voice = "en_US-lessac-medium.onnx" 
        self.short_tts = "gtts"
    
    def generate_tts(self, text: str, output_path: str, mode: str = "podcast"):
        """Podcast için Piper TTS, Shorts için gTTS"""
        try:
            if mode == "podcast":
                return self._generate_podcast_tts(text, output_path)
            else:
                return self._generate_shorts_tts(text, output_path)
        except Exception as e:
            logger.error(f"❌ Ses üretimi hatası: {str(e)}")
            return self._generate_fallback_audio(text, output_path)
    
    def _generate_podcast_tts(self, text: str, output_path: str):
        """Podcast için Piper TTS ile tok erkek ses"""
        logger.info("🎙️ PİPER TTS ile podcast sesi üretiliyor (tok erkek ses)...")
        
        # Modeli indir (cache'li)
        model_path = self._get_model_path(self.podcast_voice)
        
        # Ses oluştur
        from piper import PiperVoice
        voice = PiperVoice.load(str(model_path))
        
        # Tok ses için özel parametreler
        with open(output_path, "wb") as f:
            voice.synthesize(
                text,
                f,
                length_scale=1.15,  # Daha yavaş konuşma
                noise_scale=0.667   # Daha net ses
            )
        
        logger.info(f"✅ Podcast sesi hazır: {output_path}")
        return output_path
    
    def _generate_shorts_tts(self, text: str, output_path: str):
        """Shorts için gTTS"""
        from gtts import gTTS
        logger.info("📱 gTTS ile shorts sesi üretiliyor...")
        tts = gTTS(text=text, lang="en", slow=False)
        tts.save(output_path)
        return output_path
    
    def _get_model_path(self, model_name: str) -> Path:
        """Piper modelini indir (cache mekanizmalı)"""
        model_path = Config.MODELS_DIR / model_name
        
        if model_path.exists():
            return model_path
        
        logger.info(f"📥 Piper modeli indiriliyor: {model_name}")
        os.makedirs(Config.MODELS_DIR, exist_ok=True)
        
        # Model URL'leri
        base_url = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/"
        model_url = f"{base_url}{model_name}"
        config_url = f"{base_url}{model_name}.json"
        
        # Modeli indir
        urllib.request.urlretrieve(model_url, model_path)
        
        # Config dosyasını indir
        config_path = model_path.with_suffix(".onnx.json")
        urllib.request.urlretrieve(config_url, config_path)
        
        return model_path
    
    def _generate_fallback_audio(self, text: str, output_path: str):
        """Acil durum ses üretimi"""
        logger.warning("⚠️ Fallback ses üretimi kullanılıyor...")
        from gtts import gTTS
        tts = gTTS(text=text[:5000], lang="en", slow=True)
        tts.save(output_path)
        return output_path
