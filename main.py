import os
import re
import requests
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from urllib.parse import urlparse
from dotenv import load_dotenv
from typing import Dict, List, Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()
app = FastAPI()

# Validate environment variables
required_env_vars = ["GEMINI_API_KEY", "GOOGLE_SEARCH_API_KEY", "GOOGLE_CSE_ID"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

# Gemini setup
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("models/gemini-2.0-flash")

def extract_domain(url: str) -> Optional[str]:
    """Extract domain from URL with proper error handling."""
    try:
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception as e:
        logger.error(f"Error parsing URL {url}: {e}")
        return None

def fetch_official_news(entity):
    params = {
        "q": f"{entity} legal news and issues",
        "key": GOOGLE_SEARCH_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "num": 10
    }
    try:
        response = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
        data = response.json()
        if "items" in data:
            return [{"title": item["title"], "link": item["link"]} for item in data["items"]]
        return []
    except:
        return []

def fetch_official_documents(entity: str) -> List[Dict[str, str]]:
    """Fetch official documents with proper error handling."""
    params = {
        "q": f"{entity} (\"annual report\" OR \"financial report\") filetype:pdf",
        "key": GOOGLE_SEARCH_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "num": 10
    }

    docs = []
    try:
        response = requests.get(
            "https://www.googleapis.com/customsearch/v1",
            params=params,
            timeout=15
        )
        response.raise_for_status()
        items = response.json().get("items", [])
    except Exception as e:
        logger.error(f"Error fetching documents for {entity}: {e}")
        items = []

    for item in items:
        try:
            title = item.get("title", "Untitled Document")
            link = item.get("link", "")
            year_match = re.search(r"(20\d{2})", title) or re.search(r"(20\d{2})", link)
            year = year_match.group(1) if year_match else "Unknown"

            docs.append({
                "title": title,
                "link": link,
                "year": year
            })
        except Exception as e:
            logger.error(f"Error processing document item: {e}")

    docs.sort(key=lambda d: int(d["year"]) if d["year"].isdigit() else 0, reverse=True)
    return docs[:5]  # Limit to 5 items

def get_company_profile_from_gemini(entity: str) -> str:
    """Get company profile from Gemini with proper error handling."""
    prompt = f"""
Act as a professional analyst and provide a detailed company profile for **{entity}**.
Include:
1. Industry Sector
2. Products or Services
3. Recent Activities and Developments
4. Official Website (if available)
5. Key Financial Information
6. Leadership Team
7. Major Clients and Partnerships

Respond in clear markdown format with appropriate sections.
"""
    try:
        response = gemini_model.generate_content(prompt)
        if response and hasattr(response, 'text'):
            return response.text
        return "No data retrieved from Gemini."
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return f"Error generating profile: {str(e)}"

def generate_pdf(entity: str, content: str, official_news: List[Dict[str, str]]) -> str:
    """Generate PDF report with proper error handling."""
    try:
        # Use standard font if custom font not available
        font_name = "Helvetica"
        try:
            font_path = "DejaVuSans.ttf"
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont("DejaVu", font_path))
                font_name = "DejaVu"
        except Exception as e:
            logger.warning(f"Could not load custom font: {e}")

        filename = f"{entity.replace(' ', '_')}_summary_{datetime.now().strftime('%Y%m%d')}.pdf"
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4

        # Title
        c.setFont(font_name, 16)
        c.drawCentredString(width / 2, height - 50, f"Summary of {entity}")

        # Content
        c.setFont(font_name, 11)
        text = c.beginText(40, height - 80)

        # Split content into lines and add to PDF
        for line in content.split("\n"):
            if line.strip():
                # Simple line wrapping
                words = line.split()
                current_line = []
                for word in words:
                    if len(' '.join(current_line + [word])) < 100:
                        current_line.append(word)
                    else:
                        text.textLine(' '.join(current_line))
                        current_line = [word]
                if current_line:
                    text.textLine(' '.join(current_line))

        # Add news section if available
        if official_news:
            text.textLine("\n\nOfficial News:")
            for item in official_news:
                text.textLine(f"- {item.get('title', 'No title')}")
                text.textLine(f"  {item.get('link', 'No link')}")

        c.drawText(text)
        c.save()

        return filename
    except Exception as e:
        logger.error(f"PDF generation error: {e}")
        return ""

@app.get("/summarize/{entity}", response_model=Dict)
async def summarize_entity(entity: str):
    """Main endpoint to summarize an entity with comprehensive error handling."""
    try:
        if not entity.strip() or len(entity.strip()) < 2:
            raise HTTPException(status_code=400, detail="Entity name too short")

        # Sanitize entity name
        sanitized_entity = re.sub(r'[^\w\s-]', '', entity).strip()
        if not sanitized_entity:
            raise HTTPException(status_code=400, detail="Invalid entity name")

        logger.info(f"Processing request for entity: {sanitized_entity}")

        # Get company profile
        summary = get_company_profile_from_gemini(sanitized_entity)
        if "Error" in summary or "No data" in summary:
            raise HTTPException(status_code=500, detail=summary)

        # Extract official website if mentioned
        official_url = ""
        url_match = re.search(r"(https?://[^\s]+)", summary)
        if url_match:
            official_url = url_match.group(0)

        # Fetch additional data
        official_news = fetch_official_news(sanitized_entity)
        official_docs = fetch_official_documents(sanitized_entity)

        # Generate PDF
        pdf_file = generate_pdf(sanitized_entity, summary, official_news)
        if not pdf_file:
            raise HTTPException(status_code=500, detail="Failed to generate PDF")

        return {
            "summary": summary,
            "pdf": pdf_file,
            "official_news": official_news,
            "official_documents": official_docs
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing {entity}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/download/{entity}")
async def download_pdf(entity: str):
    """Endpoint to download generated PDF."""
    try:
        sanitized_entity = re.sub(r'[^\w\s-]', '', entity).strip()
        if not sanitized_entity:
            raise HTTPException(status_code=400, detail="Invalid entity name")

        # Find the most recent PDF for this entity
        pdf_files = [
            f for f in os.listdir()
            if f.startswith(f"{sanitized_entity.replace(' ', '_')}_summary_") and f.endswith(".pdf")
        ]

        if not pdf_files:
            raise HTTPException(status_code=404, detail="PDF not found")

        # Get the most recent file
        latest_pdf = max(pdf_files)
        if not os.path.exists(latest_pdf):
            raise HTTPException(status_code=404, detail="PDF file missing")

        return FileResponse(
            latest_pdf,
            media_type="application/pdf",
            filename=f"{sanitized_entity}_summary.pdf"
        )
    except Exception as e:
        logger.error(f"PDF download error for {entity}: {e}")
        raise HTTPException(status_code=500, detail=str(e))