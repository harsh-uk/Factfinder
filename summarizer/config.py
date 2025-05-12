import os
from dotenv import load_dotenv

load_dotenv()

REQUIRED_ENV_VARS = ["GEMINI_API_KEY", "GOOGLE_SEARCH_API_KEY", "GOOGLE_CSE_ID", "ALPHAVANTAGE_API_KEY"]
missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing:
    raise EnvironmentError(f"Missing environment variables: {', '.join(missing)}")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
ALPHAVANTAGE_API_KEY=os.getenv("ALPHAVANTAGE_API_KEY")