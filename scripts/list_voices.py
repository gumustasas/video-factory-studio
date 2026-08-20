"""List all ElevenLabs voices — run this to pick a Turkish-friendly voice."""
import os, json, requests

api_key = os.environ.get("ELEVENLABS_API_KEY", "")
if not api_key:
    raise SystemExit("ELEVENLABS_API_KEY ayarlı değil.")

r = requests.get("https://api.elevenlabs.io/v1/voices",
                 headers={"xi-api-key": api_key}, timeout=30)
r.raise_for_status()

voices = r.json().get("voices", [])
print(f"\nToplam {len(voices)} ses:\n")
print(f"{'İsim':30s} {'Voice ID':30s} {'Dil':15s} {'Aksan'}")
print("-" * 90)
for v in sorted(voices, key=lambda x: x["name"]):
    labels = v.get("labels", {})
    lang = labels.get("language", "-")
    accent = labels.get("accent", "-")
    print(f"{v['name']:30s} {v['voice_id']:30s} {lang:15s} {accent}")
