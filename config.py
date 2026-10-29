"""Read configuration without printing credentials."""
import os
from pathlib import Path
from dotenv import load_dotenv


def get_settings(url=None, key=None):
    load_dotenv(Path(__file__).with_name(".env"))
    url = (url or os.getenv("SUPABASE_URL", "")).strip().rstrip("/")
    key = (key or os.getenv("SUPABASE_SECRET_KEY", "")).strip()
    if not url.startswith("https://") or "YOUR_PROJECT" in url:
        raise ValueError("Set SUPABASE_URL to your project's HTTPS URL.")
    if not key.startswith("sb_secret_"):
        raise ValueError("Set SUPABASE_SECRET_KEY to your project's sb_secret_ key.")
    return url, key

