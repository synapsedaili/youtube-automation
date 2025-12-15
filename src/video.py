# video.py
import os
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from moviepy.video.VideoClip import ColorClip, TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.ImageClip import ImageClip

# === ÇIKTI KLASÖRLERİ ===
OUTPUT_DIR = r"C:\Users\gktg9\PycharmProjects\YouTube\output"
VIDEO_DIR = os.path.join(OUTPUT_DIR, "videos")
AUDIO_DIR = os.path.join(OUTPUT_DIR, "audio")
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

def split_text_into_lines(text: str, max_chars_per_line=60):
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        if len(current_line) + len(word) + 1 <= max_chars_per_line:
            current_line += (" " + word) if current_line else word
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

def text_to_speech_elevenlabs(text: str, output_path: str):
    """ElevenLabs ile İngilizce ses üretimi (60 sn uyumlu)."""
    if not os.environ.get("ELEVENLABS_API_KEY"):
        raise ValueError("❌ ELEVENLABS_API_KEY ayarlanmadı")

    # 150 kelimeden fazlasını kes
    words = text.split()
    if len(words) > 150:
        text = " ".join(words[:150]) + "..."

    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])

    response = client.text_to_speech.convert(
        voice_id="AZnzlk1XvdvUeBnXmlld",  # Domi
        optimize_streaming_latency="0",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_turbo_v2",
        voice_settings=VoiceSettings(
            stability=0.75,
            similarity_boost=0.75,
            style=0.0,
            use_speaker_boost=True,
        ),
    )

    with open(output_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

def create_video_from_script(script: str, idea_title: str) -> str:
    safe_name = "".join(c for c in idea_title if c.isalnum() or c in " _-")[:30]
    video_path = os.path.join(VIDEO_DIR, f"{safe_name}.mp4")
    audio_path = os.path.join(AUDIO_DIR, f"{safe_name}.mp3")

    # === 1. SES ÜRETİMİ (60 SN UYUMLU) ===
    try:
        text_to_speech_elevenlabs(script, audio_path)
    except Exception as e:
        raise RuntimeError(f"🔊 Ses üretimi hatası: {e}")

    # === 2. ARKA PLAN GÖRSELİ ===
    width, height = 1280, 720
    bg_path = "sd_background.jpg"

    if not os.path.exists(bg_path):
        raise FileNotFoundError(f"Arka plan görseli bulunamadı: {bg_path}")

    background = (
        ImageClip(bg_path)
        .resize((width, height))
        .set_duration(60)
    )

    # === 3. METİN İŞLEME ===
    lines = split_text_into_lines(script, max_chars_per_line=65)
    if not lines:
        lines = ["(No content)"]

    # === 4. SES SÜRESİ (60 SN SINIRLI) ===
    audio = AudioFileClip(audio_path)
    total_duration = min(audio.duration, 60.0)

    # === 5. METNİ ZAMANLA (KELİMEYE GÖRE) ===
    text_clips = []
    current_time = 0.0
    for line in lines:
        if current_time >= total_duration:
            break

        word_count = len(line.split())
        # İngilizce ortalama: 1 kelime = 0.35 saniye
        duration = max(2.0, min(word_count * 0.35, total_duration - current_time))

        end_time = current_time + duration

        # Metin klip oluştur
        try:
            txt_clip_main = TextClip(
                line,
                font="Arial-Bold",
                fontsize=54,
                color="white",
                size=(width - 120, None),
                method="caption"
            )
        except:
            txt_clip_main = TextClip(
                line,
                fontsize=50,
                color="white",
                size=(width - 120, None),
                method="caption"
            )

        # Hafif beyaz gölge
        txt_clip_shadow = TextClip(
            line,
            font="Arial-Bold",
            fontsize=54,
            color="white",
            size=(width - 120, None),
            method="caption"
        ).set_position(("center", height - 120 + 5)).set_opacity(0.3)

        # Birleştir
        txt_clip_final = CompositeVideoClip([
            txt_clip_shadow.set_start(current_time).set_duration(duration),
            txt_clip_main.set_start(current_time).set_duration(duration)
        ]).set_position(("center", height - 120))

        txt_clip_final = txt_clip_final.fadein(0.2).fadeout(0.2)
        text_clips.append(txt_clip_final)

        current_time = end_time

    # === 6. BİRLEŞTİR ===
    final_video = CompositeVideoClip([background] + text_clips)
    final_video = final_video.set_audio(audio).set_duration(total_duration)

    # === 7. KAYDET ===
    final_video.write_videofile(
        video_path,
        fps=24,
        audio_codec="aac",
        temp_audiofile=os.path.join(AUDIO_DIR, "temp-audio.m4a"),
        remove_temp=True,
        logger=None,
        threads=2
    )

    return video_path