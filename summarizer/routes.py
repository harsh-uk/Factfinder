import os
import re

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from summarizer.services import alpha_financials, gemini_service, google_search, pdf_generator

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
    symbol = alpha_financials.search_symbol(sanitized)
    financial_data = alpha_financials.get_quarterly_financials(symbol) if symbol else {}
    # Extract latest quarter metrics (optional, for PDF)
    latest_year = max(financial_data.keys()) if financial_data else None
    latest_q = max(financial_data[latest_year].keys()) if latest_year else None
    metrics = financial_data[latest_year][latest_q] if latest_q else {}

    pdf = pdf_generator.generate_pdf(sanitized, summary, news, metrics)

    if not pdf:
        raise HTTPException(status_code=500, detail="Failed to generate PDF")

    return {
        "summary": summary,
        "pdf": pdf,
        "official_news": news,
        "official_documents": docs,
        "financial_data": financial_data
    }


@router.get("/download/{entity}")
async def download_pdf(entity: str):
    sanitized = re.sub(r'[^\w\s-]', '', entity).strip().replace(" ", "_")
    folder = "summaries"
    matching_files = [
        f for f in os.listdir(folder)
        if f.startswith(f"{sanitized}_summary_") and f.endswith(".pdf")
    ]

    if not matching_files:
        raise HTTPException(status_code=404, detail="PDF not found")

    latest_pdf = max(matching_files)
    full_path = os.path.join(folder, latest_pdf)

    return FileResponse(full_path, media_type="application/pdf", filename=f"{sanitized}_summary.pdf")
