import os
import re
import json
import tempfile
import requests
from datetime import datetime
import pdfplumber

DATA_DIR = os.path.join("data_cache")
os.makedirs(DATA_DIR, exist_ok=True)

def extract_financial_data_from_pdf_url(pdf_url: str, entity: str) -> dict:
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(response.content)
            return extract_financial_data_from_pdf(tmp_file.name, entity)
    except Exception as e:
        return {}

def extract_financial_data_from_pdf(file_path: str, entity: str) -> dict:
    quarterly_data = {}
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if not table:
                    continue
                for row in table:
                    row = [cell.strip() if cell else "" for cell in row]
                    row_str = " ".join(row).lower()
                    if any(q in row_str for q in ["q1", "q2", "q3", "q4"]):
                        match = re.search(r"(q[1-4])\s*(20\d{2})", row_str)
                        if match:
                            quarter, year = match.groups()
                            revenue_match = re.search(r"(revenue|sales).*?(\d[\d,.]*)", row_str)
                            profit_match = re.search(r"(profit|net income).*?(\d[\d,.]*)", row_str)
                            revenue = float(revenue_match.group(2).replace(",", "")) if revenue_match else None
                            profit = float(profit_match.group(2).replace(",", "")) if profit_match else None
                            quarterly_data.setdefault(year, {})[quarter.upper()] = {
                                "revenue": revenue,
                                "profit": profit
                            }
    except Exception:
        pass
    return quarterly_data

def save_financial_data(entity: str, data: dict):
    file_path = os.path.join(DATA_DIR, f"{entity.replace(' ', '_').lower()}_financials.json")
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

def load_financial_data(entity: str) -> dict:
    file_path = os.path.join(DATA_DIR, f"{entity.replace(' ', '_').lower()}_financials.json")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return {}

def update_financial_dataset(entity: str, pdf_urls: list) -> dict:
    existing_data = load_financial_data(entity)
    updated_data = {}

    for url in pdf_urls:
        data = extract_financial_data_from_pdf_url(url, entity)
        for year, quarters in data.items():
            updated_data.setdefault(year, {}).update(quarters)

    for year, quarters in updated_data.items():
        existing_data.setdefault(year, {}).update(quarters)

    save_financial_data(entity, existing_data)
    return existing_data