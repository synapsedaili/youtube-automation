# src/script_generator.py
import os
import requests
from src.config import Config
from src.utils import setup_logging

logger = setup_logging()

def get_shorts_prompt(topic: str) -> str:
    """Shorts için 1000 karakterlik güçlü prompt."""
    return f"""
You are the narrator of 'Synapse Daily' – a channel about Cold War tech and lost futures.
Write a **YouTube Shorts script** about: {topic}

RULES:
- Start with a HOOK that grabs attention in 5 seconds: "What if you could...?" or "Imagine..."
- Include 1 PERSONAL TOUCH: "I couldn't believe this existed!" or "Shocking, right?"
- End with: "Don't forget to like, comment, and subscribe for more lost futures!"
- Tone: Thoughtful, nostalgic, curious — but FAST-PACED.
- NO markdown, NO explanations — just the script.
- TOTAL CHARACTERS: MAX 1000 (strict!).

Script:
""".strip()

def get_podcast_prompt(topic: str) -> str:
    """Podcast için 225.000 karakterlik derinlemesine prompt."""
    return f"""
You are the narrator of 'Synapse Daily', exploring Cold War oddities and unbuilt utopias.
Write a **podcast script** about: {topic}

Write EXACTLY 225,000 characters (not less, not more). This is critical.

STRUCTURE:
1. **HOOK (0:00-0:15)**: Start with a vivid, cinematic question or image. Example: "If you had 20 minutes to explore a city before vanishing forever, which would you choose? In the 1970s, Soviet architects dreamed of exactly that..."

2. **STORYTELLING**: Frame facts around a PERSON, DECISION, or CONFLICT. Example: "Meet Dr. Ivan Petrov – the engineer who risked his life to build..."

3. **TENSION & CURIOSITY**: Ask "Why?" and "What happened next?" Reveal information in layers.

4. **PERSONAL VOICE**: Use 2-3 subjective phrases: "I find this haunting...", "What strikes me is...", "I couldn't sleep after reading this..."

5. **RHYTHM**: Short sentences. Use transitions: "But here's the twist...", "Now, the real story begins..."

6. **CALL TO ACTION (LAST 15 SECONDS)**: 
   "If you enjoyed this dive into lost futures, don't forget to like, comment your thoughts below, and subscribe for more Cold War mysteries. What forgotten project should we explore next?"

7. **TONE**: Thoughtful, nostalgic, curious — never dry or academic. Speak to history lovers who crave depth but hate boredom.

RULES:
- TOTAL CHARACTERS: EXACTLY 225,000 (not less, not more)
- Language: Fluent English
- NO markdown, NO section headers — just pure script.
- END WITH CTA.

Script:
""".strip()

def generate_script(topic: str, mode: str = "shorts") -> str:
    """
    Konuya göre script üret.
    mode: 'shorts' veya 'podcast'
    """
    if mode == "shorts":
        # Shorts için kısa metin
        short_script = f"""
What if you could travel back to 1960 and witness Project Orion - the nuclear-powered spaceship that could have changed space travel forever?

In the Cold War era, scientists imagined a world where atomic bombs could propel spacecraft to distant stars. Project Orion was born from this dream.

The concept was revolutionary: drop nuclear bombs behind a massive spacecraft, and use the explosion to push it forward. It wasn't science fiction - it was real physics, real engineering.

But why was it cancelled? What were the risks? And could we build it today?

Join us next time for more Cold War mysteries. Don't forget to like, comment, and subscribe for more lost futures!
        """.strip()
        return short_script[:Config.SHORTS_CHAR_LIMIT]
else:
    script = """
Welcome to Synapse Daily. In 1960, DARPA launched its first artificial intelligence research program, marking the birth of machine intelligence as we know it.

The story begins at MIT and Stanford, where visionary scientists like John McCarthy and Marvin Minsky gathered to explore whether machines could think.

They called it "Artificial Intelligence" – a term coined by McCarthy in 1956. By 1960, DARPA was funding early AI labs with millions of dollars, believing intelligent machines were just years away.

The first projects included general problem solvers, language processing systems, and early neural networks. These weren't science fiction – they were real programs running on room-sized computers.

But reality proved more complex than expected. The "AI winter" would come in the 1970s when promises outpaced progress.

Yet that 1960 spark ignited a revolution. Today's AI owes its existence to those Cold War pioneers who dared to imagine thinking machines.

What if AI research had received unlimited funding from the start? How different would our world be today?

If you enjoyed this dive into AI's origins, don't forget to like, comment, and subscribe for more Cold War mysteries.
"""
    # 15 dakika ≈ 22.500 karakter (gTTS limiti içinde)
    return script[:22500] 
