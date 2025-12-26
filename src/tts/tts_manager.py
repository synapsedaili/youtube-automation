# src/tts/tts_manager.py
import os
import logging
from pathlib import Path
from src.config import Config
from src.utils import setup_logging

logger = setup_logging()

class TTSManager:
    """Limitsiz ses yönetimi sistemi"""
    
    def __init__(self):
        self.short_tts = "gtts"  # Shorts için gTTS
        self.podcast_tts = "piper"  # Podcast için Piper TTS
        self.voice_models = {
            "piper": {
                "male": "en_US-lessac-medium.onnx",  # Erkek ses
                "female": "en_US-amy-low.onnx"  # Kadın ses
            },
            "coqui": {
                "male": "tts_models/en/ljspeech/vits",
                "female": "tts_models/en/ljspeech/tacotron2-DDC"
            }
        }
    
    def generate_tts(self, text: str, output_path: str, mode: str = "shorts", voice_type: str = "male"):
        """
        Ses üretimi:
        - Shorts: gTTS (sınırlandırılmış ama kısa metin için yeterli)
        - Podcast: Piper TTS (limitsiz, offline)
        """
        try:
            if mode == "shorts":
                return self._generate_gtts(text, output_path)
            else:
                return self._generate_piper(text, output_path, voice_type)
        except Exception as e:
            logger.error(f"❌ Ses üretimi hatası: {str(e)}")
            
            # Fallback mekanizması
            logger.info("🔄 Fallback ses üretimi deneniyor...")
            try:
                return self._generate_fallback_audio(text, output_path)
            except:
                logger.critical("🔥 SES ÜRETİMİ TAMAMEN BAŞARISIZ!")
                raise
    
    def _generate_gtts(self, text: str, output_path: str):
        """Shorts için gTTS (kısa metinler için yeterli)"""
        from gtts import gTTS
        logger.info("🎙️ gTTS ile shorts sesi üretiliyor...")
        tts = gTTS(text=text, lang="en", slow=False)
        tts.save(output_path)
        return output_path
    
    def _generate_piper(self, text: str, output_path: str, voice_type: str = "male"):
        """Podcast için Piper TTS (limitsiz, offline)"""
        logger.info(f"🎙️ Piper TTS ile podcast sesi üretiliyor ({voice_type} ses)...")
        
        # Model yolunu al
        model_name = self.voice_models["piper"][voice_type]
        model_path = Config.MODELS_DIR / model_name
        
        # Modeli indir (eğer yoksa)
        self._download_piper_model(model_path, voice_type)
        
        # Ses oluştur
        from piper import PiperVoice
        voice = PiperVoice.load(str(model_path))
        
        with open(output_path, "wb") as f:
            voice.synthesize(text, f)
        
        logger.info(f"✅ Podcast sesi hazır: {output_path}")
        return output_path
    
    def _download_piper_model(self, model_path: Path, voice_type: str):
        """Piper modelini indir (cache'li)"""
        if model_path.exists():
            return
        
        logger.info(f"📥 Piper {voice_type} modeli indiriliyor...")
        import urllib.request
        
        # Erkek ses modeli (daha yavaş ve lgun)
        if voice_type == "male":
            url = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx"
            config_url = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json"
        else:
            url = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/amy/low/en_US-amy-low.onnx"
            config_url = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/amy/low/en_US-amy-low.onnx.json"
        
        # Modeli indir
        os.makedirs(Config.MODELS_DIR, exist_ok=True)
        urllib.request.urlretrieve(url, model_path)
        
        # Config dosyasını indir
        config_path = model_path.with_suffix(".onnx.json")
        urllib.request.urlretrieve(config_url, config_path)
    
    def _generate_fallback_audio(self, text: str, output_path: str):
        """Acil durum ses üretimi"""
        logger.warning("⚠️ Fallback ses üretimi kullanılıyor...")
        from gtts import gTTS
        tts = gTTS(text=text[:5000], lang="en", slow=True)  # Sadece ilk 5000 karakter
        tts.save(output_path)
        return output_path
