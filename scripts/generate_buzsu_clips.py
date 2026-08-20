"""
Buzsu AI Video Clip Generator — Kling v3 via fal.ai
Generates 5-second cinematic water brand clips for each scene.

Usage (local):
    export FAL_KEY=your_key_here
    python scripts/generate_buzsu_clips.py

Usage (GitHub Actions):
    Triggered by generate-buzsu-video workflow.

Output: projects/buzsu-hook-reel/assets/video/
Total cost estimate: ~$0.60 (6 clips × $0.10 each, Kling v3 standard)
"""

from __future__ import annotations

import os
import json
import time
import requests
from pathlib import Path

API_KEY = os.environ.get("FAL_KEY", "")
OUTPUT_DIR = Path("projects/buzsu-hook-reel/assets/video")
MODEL = "fal-ai/kling-video/v3/standard/text-to-video"

# -----------------------------------------------------------------------
# Clip definitions — each maps to a Buzsu video scene
# Kling v3 prompt structure: subject + environment + motion + mood + camera
# -----------------------------------------------------------------------
CLIPS = [
    {
        "id": "01-hook",
        "scene": "hook",
        "duration": "5",
        "aspect_ratio": "9:16",
        "prompt": (
            "Crystal clear water droplets falling in slow motion against deep navy blue background, "
            "macro close-up, each drop refracting light with prismatic clarity, "
            "cinematic cyan accent light from below, ultra-premium water brand aesthetic, "
            "shallow depth of field, smooth deceleration, 4K quality"
        ),
    },
    {
        "id": "02-tds-meter",
        "scene": "sehir-tds",
        "duration": "5",
        "aspect_ratio": "9:16",
        "prompt": (
            "Modern digital TDS meter being dipped into glass of tap water on marble counter, "
            "display showing high numbers, orange warning light reflection on water surface, "
            "clean minimalist laboratory aesthetic, dark blue background, "
            "slow deliberate camera push-in to meter display, cinematic depth"
        ),
    },
    {
        "id": "03-comparison",
        "scene": "karsilastirma",
        "duration": "5",
        "aspect_ratio": "9:16",
        "prompt": (
            "Two identical crystal glasses side by side, one with murky yellowish tap water and one with perfectly clear pure water, "
            "dramatic side lighting revealing the difference, deep ocean blue background, "
            "slow camera pan left to right comparing both glasses, "
            "premium product photography style, cinematic color grading"
        ),
    },
    {
        "id": "04-buzsu-pure",
        "scene": "buzsu-stat",
        "duration": "5",
        "aspect_ratio": "9:16",
        "prompt": (
            "Pure crystal clear water pouring from above into a glass, "
            "perfect clarity with zero particles, cyan-tinted light creating ethereal glow, "
            "deep navy blue background, slow motion pour, water surface perfectly still and mirror-like, "
            "ultra premium water brand, 4K macro cinematography"
        ),
    },
    {
        "id": "05-health-concern",
        "scene": "neden-onemli",
        "duration": "5",
        "aspect_ratio": "9:16",
        "prompt": (
            "Close-up of white limescale deposits forming on modern chrome kitchen faucet and pipe, "
            "dramatic lighting revealing mineral buildup texture, warm amber accent light highlighting problem areas, "
            "dark background, slow camera zoom revealing detail, "
            "cinematic quality, health awareness visual"
        ),
    },
    {
        "id": "06-cta-brand",
        "scene": "cta",
        "duration": "5",
        "aspect_ratio": "9:16",
        "prompt": (
            "Premium Buzsu water bottle emerging from deep blue water with ripple effect, "
            "crystal clear water surrounding it, cyan light from below creating halo effect, "
            "slow motion upward camera move, hero product shot, "
            "deep navy blue to cyan gradient background, premium brand commercial quality"
        ),
    },
]


def submit_clip(clip: dict, headers: dict) -> tuple[str, str] | None:
    """Submit clip to fal.ai queue and return (status_url, response_url)."""
    payload = {
        "prompt": clip["prompt"],
        "duration": clip["duration"],
        "aspect_ratio": clip["aspect_ratio"],
    }
    resp = requests.post(
        f"https://queue.fal.run/{MODEL}",
        headers=headers,
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["status_url"], data["response_url"]


def poll_and_download(clip_id: str, status_url: str, response_url: str,
                      headers: dict, out_path: Path) -> bool:
    """Poll until done, then download video."""
    print(f"  Polling [{clip_id}]", end="", flush=True)
    for _ in range(60):  # max 5 minutes
        time.sleep(5)
        print(".", end="", flush=True)
        status_resp = requests.get(status_url, headers=headers, timeout=15)
        status_resp.raise_for_status()
        status = status_resp.json().get("status", "UNKNOWN")
        if status == "COMPLETED":
            break
        if status in ("FAILED", "CANCELLED"):
            print(f"\n  ERROR: {clip_id} {status}")
            return False

    print(" done")
    result_resp = requests.get(response_url, headers=headers, timeout=30)
    result_resp.raise_for_status()
    video_url = result_resp.json()["video"]["url"]

    video_bytes = requests.get(video_url, timeout=120).content
    out_path.write_bytes(video_bytes)
    size_mb = len(video_bytes) / 1_048_576
    print(f"  ✓ {out_path.name} ({size_mb:.1f} MB)")
    return True


def main() -> None:
    if not API_KEY:
        raise SystemExit("FAL_KEY ortam değişkeni ayarlı değil.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    headers = {
        "Authorization": f"Key {API_KEY}",
        "Content-Type": "application/json",
    }

    print(f"\n=== Buzsu AI Video Clip Generator ===")
    print(f"Model: {MODEL}")
    print(f"Clips: {len(CLIPS)} × 5s  (~${len(CLIPS) * 0.10:.2f} tahmini maliyet)\n")

    # Submit all clips first (parallel queue)
    jobs: list[dict] = []
    for clip in CLIPS:
        out_path = OUTPUT_DIR / f"{clip['id']}.mp4"
        if out_path.exists():
            print(f"  SKIP {clip['id']} (zaten mevcut)")
            continue
        print(f"  Submitting [{clip['id']}]...")
        try:
            status_url, response_url = submit_clip(clip, headers)
            jobs.append({**clip, "status_url": status_url,
                         "response_url": response_url, "out_path": out_path})
            time.sleep(1)
        except Exception as e:
            print(f"  SUBMIT FAILED [{clip['id']}]: {e}")

    print(f"\n{len(jobs)} clip kuyruğa alındı. İndirme başlıyor...\n")

    # Poll and download
    ok = 0
    for job in jobs:
        try:
            if poll_and_download(job["id"], job["status_url"],
                                 job["response_url"], headers, job["out_path"]):
                ok += 1
        except Exception as e:
            print(f"\n  ERROR [{job['id']}]: {e}")

    # Save clip manifest
    manifest = {
        "script_key": "buzsu-hook-reel",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model": MODEL,
        "clips": [
            {"id": c["id"], "scene": c["scene"],
             "path": str(OUTPUT_DIR / f"{c['id']}.mp4"),
             "prompt": c["prompt"][:80] + "..."}
            for c in CLIPS
        ],
    }
    manifest_path = OUTPUT_DIR / "clip_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2))

    print(f"\n{ok}/{len(jobs)} clip üretildi → {OUTPUT_DIR}")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
