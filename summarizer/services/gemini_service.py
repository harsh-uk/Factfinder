import google.generativeai as genai

from summarizer.config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("models/gemini-2.0-flash")


def get_company_profile(entity: str) -> str:
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
Don't give extra response at the start like okay here is the summary, etc.
"""
    try:
        response = gemini_model.generate_content(prompt)
        return getattr(response, "text", "No data retrieved from Gemini.")
    except Exception as e:
        return f"Error generating profile: {str(e)}"
