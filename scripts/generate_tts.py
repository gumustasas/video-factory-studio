"""
Turkish TTS Generator — ElevenLabs Multilingual v2
Generates voice-over audio for Buzsu/Suvesu video scripts.

Usage (local):
    export ELEVENLABS_API_KEY=sk_...
    python scripts/generate_tts.py

Usage (GitHub Actions):
    Triggered automatically by the generate-turkish-tts workflow.

Output: projects/<script_key>/assets/audio/
"""

from __future__ import annotations

import os
import json
import time
import requests
from pathlib import Path

# --------------------------------------------------------------------------- #
# CONFIG
# --------------------------------------------------------------------------- #

API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
SCRIPT_KEY = os.environ.get("SCRIPT_KEY", "buzsu-hook-reel")

# ElevenLabs voice IDs — Multilingual v2 supports Turkish natively
# Using "Serhan" (Turkish male, energetic) or "Freya" (multilingual female)
# Run: python scripts/list_voices.py  to see all available voices
VOICE_CONFIG = {
    "buzsu-hook-reel": {
        "voice_id": "pqHfZKP75CvOlQylNhV4",  # Bill — güçlü erkek ses, enerjik
        "model_id": "eleven_multilingual_v2",
        "stability": 0.45,
        "similarity_boost": 0.80,
        "style": 0.35,  # biraz daha ekspresif
    },
    "suvesu-istanbul": {
        "voice_id": "pqHfZKP75CvOlQylNhV4",
        "model_id": "eleven_multilingual_v2",
        "stability": 0.5,
        "similarity_boost": 0.75,
        "style": 0.2,
    },
}

# Video narration scripts (Turkish)
SCRIPTS = {
    "buzsu-hook-reel": [
        {
            "id": "hook",
            "text": "Musluğunuzdan ne geliyor? TDS testinin sonuçları sizi şaşırtacak.",
            "out_path": "projects/buzsu-hook-reel/assets/audio/01-hook.mp3",
        },
        {
            "id": "sehir-tds",
            "text": "İstanbul musluk suyunun TDS değeri üç yüz yirmi ppm. Bu ne anlama geliyor?",
            "out_path": "projects/buzsu-hook-reel/assets/audio/02-sehir-tds.mp3",
        },
        {
            "id": "karsilastirma",
            "text": "İşte karşılaştırma: Musluk suyu üç yüz yirmi, Buzsu yirmi sekiz, WHO sınırı beş yüz, ideal değer ise elli ppm.",
            "out_path": "projects/buzsu-hook-reel/assets/audio/03-karsilastirma.mp3",
        },
        {
            "id": "buzsu-stat",
            "text": "Buzsu: yalnızca yirmi sekiz ppm. Musluk suyundan yüzde doksanbir daha temiz.",
            "out_path": "projects/buzsu-hook-reel/assets/audio/04-buzsu-stat.mp3",
        },
        {
            "id": "neden-onemli",
            "text": "Yüksek TDS kireçlenmeye, metalik tada ve boru aşınmasına neden olur. Aileni koru.",
            "out_path": "projects/buzsu-hook-reel/assets/audio/05-neden-onemli.mp3",
        },
        {
            "id": "cta",
            "text": "Buzsu ile fark yarat. Link biyografide.",
            "out_path": "projects/buzsu-hook-reel/assets/audio/06-cta.mp3",
        },
    ],
}


# --------------------------------------------------------------------------- #
# HELPERS
# --------------------------------------------------------------------------- #

def generate_segment(text: str, out_path: str, voice_cfg: dict) -> bool:
    """Call ElevenLabs TTS API and write audio to out_path."""
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_cfg['voice_id']}"
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    payload = {
        "text": text,
        "model_id": voice_cfg["model_id"],
        "voice_settings": {
            "stability": voice_cfg.get("stability", 0.5),
            "similarity_boost": voice_cfg.get("similarity_boost", 0.75),
            "style": voice_cfg.get("style", 0.0),
        },
    }

    response = requests.post(url, headers=headers, json=payload,
                             params={"output_format": "mp3_44100_128"}, timeout=120)
    if response.status_code != 200:
        print(f"  ERROR {response.status_code}: {response.text[:200]}")
        return False

    path.write_bytes(response.content)
    size_kb = len(response.content) // 1024
    print(f"  ✓ {path.name} ({size_kb} KB)")
    return True


def save_manifest(script_key: str, segments: list[dict]) -> None:
    """Write an audio manifest JSON so the video pipeline knows where each clip is."""
    manifest = {
        "script_key": script_key,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "voice_model": "eleven_multilingual_v2",
        "language": "tr",
        "segments": [
            {"id": s["id"], "text": s["text"], "audio_path": s["out_path"]}
            for s in segments
        ],
    }
    out = Path(f"projects/{script_key}/assets/audio/manifest.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(f"\n  Manifest: {out}")


# --------------------------------------------------------------------------- #
# MAIN
# --------------------------------------------------------------------------- #

def main() -> None:
    if not API_KEY:
        raise SystemExit("ELEVENLABS_API_KEY ortam değişkeni ayarlı değil.")

    segments = SCRIPTS.get(SCRIPT_KEY)
    if not segments:
        raise SystemExit(f"Bilinmeyen script: {SCRIPT_KEY}. Mevcut: {list(SCRIPTS)}")

    voice_cfg = VOICE_CONFIG.get(SCRIPT_KEY, VOICE_CONFIG["buzsu-hook-reel"])

    print(f"\n=== Turkish TTS Generation: {SCRIPT_KEY} ===")
    print(f"Voice: {voice_cfg['voice_id']} | Model: {voice_cfg['model_id']}\n")

    ok = 0
    for seg in segments:
        print(f"[{seg['id']}] {seg['text'][:60]}...")
        if generate_segment(seg["text"], seg["out_path"], voice_cfg):
            ok += 1
        time.sleep(0.5)  # rate limit

    save_manifest(SCRIPT_KEY, segments)
    print(f"\n{ok}/{len(segments)} segment üretildi.")


if __name__ == "__main__":
    main()
