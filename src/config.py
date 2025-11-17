from dotenv import load_dotenv
from pathlib import Path
import os

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=False)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise RuntimeError(
        "SUPABASE_URL or SUPABASE_SERVICE_KEY is not set. "
        "Create a .env file based on .env.example and fill in the values."
    )

if not OPENAI_API_KEY:
    # Not fatal, but warn early.
    print(
        "[WARNING] OPENAI_API_KEY is not set. "
        "LLM features will not work until you set it in .env."
    )
