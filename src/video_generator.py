# src/video_generator.py
import os
import tempfile
import shutil
from pathlib import Path
import numpy as np
import asyncio
import edge_tts
from moviepy.editor import ColorClip, CompositeVideoClip, AudioFileClip, ImageClip
from PIL import Image, ImageDraw, ImageFont
from src.config import Config
from src.utils import setup_logging

logger = setup_logging()

async def generate_voice_with_edge_tts(text: str, output_path: str):
    """Edge TTS ile kaliteli ses üretir (ücretsiz)."""
    logger.info("🎧 Edge TTS ile ses üretiliyor...")
    communicate = edge_tts.Communicate(text, "en-US-GuyNeural")
    await communicate.save(output_path)
    logger.info(f"✅ Ses dosyası hazır: {output_path}")

def create_text_image_shorts(text: str, width: int, height: int, fontsize: int = 1000) -> Image.Image:
    """Shorts: Siyah yazı + beyaz gölge (sd_background.jpg üzerine)."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", fontsize)
    except:
        font = ImageFont.load_default()
    
    # Metni kırp
    text = text[:50]
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Ölçeklendirme
    max_width = width * 0.9
    if text_width > max_width:
        scale = max_width / text_width
        fontsize = int(fontsize * scale)
        try:
            font = ImageFont.truetype("arial.ttf", fontsize)
        except:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), text, font=font)
    
    # Pozisyon hesaplama
    x = (width - (bbox[2] - bbox[0])) // 2
    y = (height - (bbox[3] - bbox[1])) // 2
    
    # Siyah yazı + beyaz gölge
    draw.text((x, y), text, font=font, fill=(0, 0, 0, 255), stroke_width=3, stroke_fill=(255, 255, 255, 255))
    return img

def create_text_image_podcast(text: str, width: int, height: int, fontsize: int = 60) -> Image.Image:
    """Podcast: Siyah ekran üzerine beyaz yazı (akışlı)."""
    img = Image.new("RGB", (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", fontsize)
    except:
        font = ImageFont.load_default()
    
    # Metni satırlara böl
    lines = []
    max_line_width = width - 200
    
    for paragraph in text.split('\n'):
        words = paragraph.split()
        current_line = ""
        for word in words:
            test_line = current_line + (" " + word if current_line else word)
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] <= max_line_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
    
    # Satırları yerleştir
    y_offset = 50
    line_height = fontsize + 10
    
    for line in lines:
        if y_offset > height - 100:
            break
        draw.text((50, y_offset), line, font=font, fill=(255, 255, 255))
        y_offset += line_height
    
    return img

def create_shorts_video(audio_path: str, script: str, output_path: str):
    """1 dk'lık Shorts videosu (dikey)."""
    logger.info("🎥 Shorts videosu üretiliyor...")
    
    # Ses ve süre
    audio = AudioFileClip(audio_path)
    total_duration = min(audio.duration, Config.SHORTS_DURATION)
    
    # Arka plan (sd_background.jpg)
    width, height = 1080, 1920
    bg_path = Config.BASE_DIR / "sd_background.jpg"
    
    if bg_path.exists():
        from PIL import Image as PilImage
        def resize_frame(frame):
            img = PilImage.fromarray(frame)
            return np.array(img.resize((width, height), PilImage.LANCZOS))
        
        background = ImageClip(str(bg_path))
        background = background.fl_image(resize_frame).set_duration(total_duration)
    else:
        logger.warning("⚠️ sd_background.jpg bulunamadı, siyah arka plan kullanılıyor")
        background = ColorClip((width, height), (0, 0, 0), duration=total_duration)
    
    # Metni böl (6 kelime parçaları)
    words = script.split()
    chunks = [" ".join(words[i:i+6]) for i in range(0, len(words), 6)]
    
    # Yazı klipleri
    text_clips = []
    start_time = 0.0
    speed_factor = 0.585
    min_duration = 1.5
    
    for chunk in chunks:
        if start_time >= total_duration:
            break
        
        word_count = len(chunk.split())
        duration = max(min_duration, min(word_count * speed_factor, total_duration - start_time))
        
        text_img = create_text_image_shorts(chunk, width, height, fontsize=1000)
        img_path = f"/tmp/text_shorts_{abs(hash(chunk))}.png"
        text_img.save(img_path)
        
        txt_clip = ImageClip(img_path).set_duration(duration).set_start(start_time)
        text_clips.append(txt_clip)
        start_time += duration
    
    # Birleştir
    final_video = CompositeVideoClip([background] + text_clips)
    final_video = final_video.set_audio(audio).set_duration(total_duration)
    
    # Kaydet
    final_video.write_videofile(
        str(output_path),
        fps=24,
        audio_codec="aac",
        temp_audiofile=str(Path(output_path).with_suffix(".m4a")),
        remove_temp=True,
        logger=None,
        threads=4
    )
    
    logger.info(f"✅ Shorts videosu hazır: {output_path}")
    return output_path

def create_podcast_video(audio_path: str, script: str, output_path: str):
    """15 dk'lık podcast videosu (yatay)."""
    logger.info("🎥 Podcast videosu üretiliyor...")
    
    # Ses ve süre
    audio = AudioFileClip(audio_path)
    total_duration = min(audio.duration, Config.PODCAST_DURATION)
    
    # Arka plan (siyah)
    width, height = 1920, 1080
    background = ColorClip((width, height), (0, 0, 0), duration=total_duration)
    
    # Metni böl (100 kelime blokları)
    words = script.split()
    chunks = [" ".join(words[i:i+100]) for i in range(0, len(words), 100)]
    
    # Yazı klipleri
    text_clips = []
    start_time = 0.0
    speed_factor = 0.4
    min_duration = 4.0
    
    for chunk in chunks:
        if start_time >= total_duration:
            break
        
        word_count = len(chunk.split())
        duration = max(min_duration, min(word_count * speed_factor, total_duration - start_time))
        
        text_img = create_text_image_podcast(chunk, width, height, fontsize=60)
        img_path = f"/tmp/text_podcast_{abs(hash(chunk))}.png"
        text_img.save(img_path)
        
        txt_clip = ImageClip(img_path).set_duration(duration).set_start(start_time)
        text_clips.append(txt_clip)
        start_time += duration
    
    # Birleştir
    final_video = CompositeVideoClip([background] + text_clips)
    final_video = final_video.set_audio(audio).set_duration(total_duration)
    
    # Kaydet
    final_video.write_videofile(
        str(output_path),
        fps=24,
        audio_codec="aac",
        temp_audiofile=str(Path(output_path).with_suffix(".m4a")),
        remove_temp=True,
        logger=None,
        threads=4
    )
    
    logger.info(f"✅ Podcast videosu hazır: {output_path}")
    return output_path
