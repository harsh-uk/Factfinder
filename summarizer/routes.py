import re
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from summarizer.services import gemini_service, google_search, pdf_generator

router = APIRouter()

@router.get("/summarize/{entity}")
async def summarize_entity(entity: str):
    if not entity.strip() or len(entity.strip()) < 2:
        raise HTTPException(status_code=400, detail="Entity name too short")
    
    sanitized = re.sub(r'[^\w\s-]', '', entity).strip()
    if not sanitized:
        raise HTTPException(status_code=400, detail="Invalid entity name")

    summary = gemini_service.get_company_profile(sanitized)
    if "Error" in summary or "No data" in summary:
        raise HTTPException(status_code=500, detail=summary)

    news = google_search.fetch_news(sanitized)
    docs = google_search.fetch_documents(sanitized)
    pdf = pdf_generator.generate_pdf(sanitized, summary, news)
    if not pdf:
        raise HTTPException(status_code=500, detail="Failed to generate PDF")

    return {
        "summary": summary,
        "pdf": pdf,
        "official_news": news,
        "official_documents": docs
    }

@router.get("/download/{entity}")
async def download_pdf(entity: str):
    sanitized = re.sub(r'[^\w\s-]', '', entity).strip()
    pdf_files = [f for f in os.listdir() if f.startswith(f"{sanitized.replace(' ', '_')}_summary_") and f.endswith(".pdf")]
    if not pdf_files:
        raise HTTPException(status_code=404, detail="PDF not found")
    latest_pdf = max(pdf_files)
    return FileResponse(latest_pdf, media_type="application/pdf", filename=f"{sanitized}_summary.pdf")