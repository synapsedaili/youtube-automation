# src/video_generator.py
import os
import logging
from pathlib import Path
from moviepy.editor import (
    ColorClip, TextClip, CompositeVideoClip, AudioFileClip
)
from src.config import Config
from src.utils import setup_logging, sanitize_filename

logger = setup_logging()

def split_script_into_chunks(script: str, max_chars=120) -> list:
    """Metni ekran sığacak şekilde kırpar."""
    words = script.split()
    chunks = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 <= max_chars:
            current = current + " " + word if current else word
        else:
            chunks.append(current)
            current = word
    if current:
        chunks.append(current)
    return chunks

def create_shorts_video(audio_path: str, script: str, output_path: str):
    """1 dakikalık Shorts videosu üretir."""
    logger.info("🎥 Shorts videosu üretiliyor...")
    
    # 1. Ses süresini al
    audio = AudioFileClip(audio_path)
    total_duration = min(audio.duration, Config.SHORTS_DURATION)
    
    # 2. Metni kır
    lines = split_script_into_chunks(script, max_chars=80)
    if not lines:
        lines = ["(No content)"]
    
    # 3. Arka plan (siyah)
    width, height = 1080, 1920  # Shorts formatı
    background = ColorClip(size=(width, height), color=(0, 0, 0), duration=total_duration)
    
    # 4. Yazı klipleri
    text_clips = []
    start_time = 0.0
    for line in lines:
        if start_time >= total_duration:
            break
        
        # Satır süresi
        word_count = len(line.split())
        duration = max(1.5, min(word_count * 0.35, total_duration - start_time))
        end_time = start_time + duration
        
        # Beyaz yazı
        try:
            txt_clip = TextClip(
                line,
                font="Arial-Bold",
                fontsize=60,
                color="white",
                size=(width - 100, None),
                method="caption"
            ).set_position(("center", height - 400))
        except:
            txt_clip = TextClip(
                line,
                fontsize=50,
                color="white",
                size=(width - 100, None),
                method="caption"
            ).set_position(("center", height - 400))
        
        # Zaman ayarla
        txt_clip = (
            txt_clip
            .set_start(start_time)
            .set_duration(duration)
            .fadein(0.2)
            .fadeout(0.2)
        )
        text_clips.append(txt_clip)
        start_time = end_time
    
    # 5. Birleştir
    final_video = CompositeVideoClip([background] + text_clips)
    final_video = final_video.set_audio(audio).set_duration(total_duration)
    
    # 6. Kaydet
    final_video.write_videofile(
        output_path,
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
    """15 dakikalık podcast videosu üretir."""
    logger.info("🎥 Podcast videosu üretiliyor...")
    
    # 1. Ses süresini al
    audio = AudioFileClip(audio_path)
    total_duration = min(audio.duration, Config.PODCAST_DURATION)
    
    # 2. Metni kır
    lines = split_script_into_chunks(script, max_chars=110)
    if not lines:
        lines = ["(No content)"]
    
    # 3. Arka plan (siyah)
    width, height = 1920, 1080  # Full HD
    background = ColorClip(size=(width, height), color=(0, 0, 0), duration=total_duration)
    
    # 4. Yazı klipleri
    text_clips = []
    start_time = 0.0
    for line in lines:
        if start_time >= total_duration:
            break
        
        # Satır süresi
        word_count = len(line.split())
        duration = max(3.0, min(word_count * 0.4, total_duration - start_time))
        end_time = start_time + duration
        
        # Beyaz yazı
        try:
            txt_clip = TextClip(
                line,
                font="Arial-Bold",
                fontsize=56,
                color="white",
                size=(width - 200, None),
                method="caption"
            ).set_position(("center", height - 200))
        except:
            txt_clip = TextClip(
                line,
                fontsize=50,
                color="white",
                size=(width - 200, None),
                method="caption"
            ).set_position(("center", height - 200))
        
        # Zaman ayarla
        txt_clip = (
            txt_clip
            .set_start(start_time)
            .set_duration(duration)
            .fadein(0.3)
            .fadeout(0.3)
        )
        text_clips.append(txt_clip)
        start_time = end_time
    
    # 5. Birleştir
    final_video = CompositeVideoClip([background] + text_clips)
    final_video = final_video.set_audio(audio).set_duration(total_duration)
    
    # 6. Kaydet
    final_video.write_videofile(
        output_path,
        fps=24,
        audio_codec="aac",
        temp_audiofile=str(Path(output_path).with_suffix(".m4a")),
        remove_temp=True,
        logger=None,
        threads=4
    )
    
    logger.info(f"✅ Podcast videosu hazır: {output_path}")
    return output_path