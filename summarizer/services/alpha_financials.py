import requests

from summarizer.config import ALPHAVANTAGE_API_KEY

API_KEY = ALPHAVANTAGE_API_KEY
BASE_URL = "https://www.alphavantage.co/query"


def search_symbol(company_name: str) -> str:
    known = {
        # Technology
        "apple": "AAPL",
        "microsoft": "MSFT",
        "amazon": "AMZN",
        "meta": "META",
        "facebook": "META",
        "alphabet": "GOOGL",
        "google": "GOOGL",
        "tesla": "TSLA",
        "netflix": "NFLX",
        "nvidia": "NVDA",
        "ibm": "IBM",
        "oracle": "ORCL",
        "intel": "INTC",
        "cisco": "CSCO",
        "adobe": "ADBE",
        "salesforce": "CRM",
        "amd": "AMD",
        "qualcomm": "QCOM",
        "paypal": "PYPL",
        "twitter": "X",
        "x": "X",
        "snap": "SNAP",
        "snapchat": "SNAP",
        # E-commerce & Internet
        "alibaba": "BABA",
        "baidu": "BIDU",
        "tencent": "TCEHY",
        "jd.com": "JD",
        "jd": "JD",
        "pinduoduo": "PDD",
        "pdd": "PDD",
        "meituan": "MPNGF",
        "mercadolibre": "MELI",
        "coupang": "CPNG",
        "rakuten": "RKUNY",
        "sea limited": "SE",
        "shopee": "SE",
        "grab": "GRAB",
        "gojek": "PRIVATE",
        "tokopedia": "PRIVATE",
        "flipkart": "WMT",  # Owned by Walmart
        "ozon": "OZON",
        "vk": "VKCO",
        "mail.ru": "VKCO",
        "naver": "035420.KS",
        "kakao": "035720.KS",
        "line": "LN",
        "weibo": "WB",
        "bytedance": "PRIVATE",
        "tiktok": "PRIVATE",
        "lazada": "BABA",  # Owned by Alibaba

        # Software & SaaS
        "sap": "SAP",
        "atlassian": "TEAM",
        "synopsys": "SNPS",
        "cadence": "CDNS",
        "ansys": "ANSS",
        "autodesk": "ADSK",
        "dassault systemes": "DASTY",
        "siemens plm": "SIEGY",
        "ptc": "PTC",
        "bentley systems": "BSY",
        "hubspot": "HUBS",
        "zendesk": "PRIVATE",  # Taken private
        "freshworks": "FRSH",
        "zoho": "PRIVATE",
        "slack": "CRM",  # Acquired by Salesforce
        "tableau": "CRM",  # Acquired by Salesforce
        "mulesoft": "CRM",  # Acquired by Salesforce
        "zuora": "ZUO",
        "coupa": "PRIVATE",  # Taken private
        "qualtrics": "XM",
        "smartsheet": "SMAR",
        "asana": "ASAN",
        "monday.com": "MNDY",
        "monday": "MNDY",
        "notion": "PRIVATE",
        "zoom": "ZM",
        "uber": "UBER",
        "lyft": "LYFT",
        "airbnb": "ABNB",
        "roblox": "RBLX",
        "spotify": "SPOT",
        "palantir": "PLTR",
        "dell": "DELL",
        "hp": "HPQ",
        "hewlett packard": "HPQ",
        "broadcom": "AVGO",
        "texas instruments": "TXN",
        "ti": "TXN",
        "micron": "MU",
        "micron technology": "MU",
        "intuit": "INTU",
        "autodesk": "ADSK",
        "electronic arts": "EA",
        "ea": "EA",
        "activision blizzard": "ATVI",
        "unity": "U",
        "unity software": "U",
        "twilio": "TWLO",
        "shopify": "SHOP",
        "square": "SQ",
        "block": "SQ",
        "vmware": "VMW",
        "servicenow": "NOW",
        "workday": "WDAY",
        "splunk": "SPLK",
        "snowflake": "SNOW",
        "datadog": "DDOG",
        "crowdstrike": "CRWD",
        "zscaler": "ZS",
        "okta": "OKTA",
        "palo alto networks": "PANW",
        "fortinet": "FTNT",
        "docusign": "DOCU",
        "mongodb": "MDB",
        "cloudflare": "NET",
        "akamai": "AKAM",
        "dropbox": "DBX",
        "box": "BOX",
        "juniper networks": "JNPR",
        "juniper": "JNPR",
        "ericsson": "ERIC",
        "nokia": "NOK",
        "netapp": "NTAP",
        "western digital": "WDC",
        "seagate": "STX",
        "logitech": "LOGI",
        "lenovo": "LNVGY",
        "asus": "ASUUY",
        "asustek": "ASUUY",

        # IT Services & Consulting
        "wipro": "WIT",
        "infosys": "INFY",
        "tata consultancy services": "TCS.NS",
        "tcs": "TCS.NS",
        "cognizant": "CTSH",
        "accenture": "ACN",
        "capgemini": "CAPMF",
        "hcl technologies": "HCLTECH.NS",
        "hcl": "HCLTECH.NS",
        "tech mahindra": "TECHM.NS",
        "ibm global services": "IBM",
        "mindtree": "MINDTREE.NS",
        "deloitte": "PRIVATE",
        "pwc": "PRIVATE",
        "ey": "PRIVATE",
        "kpmg": "PRIVATE",
        "cgi": "GIB",
        "epam systems": "EPAM",
        "epam": "EPAM",
        "dxc technology": "DXC",
        "dxc": "DXC",
        "genpact": "G",
        "luxoft": "LXFT",
        "atos": "AEXAY",
        "ntt data": "NTDTY",
        "fujitsu": "FJTSY",
        "cdw": "CDW",

        # Semiconductor & Electronics
        "taiwan semiconductor": "TSM",
        "tsmc": "TSM",
        "asml": "ASML",
        "applied materials": "AMAT",
        "lam research": "LRCX",
        "kla": "KLAC",
        "tokyo electron": "TOELY",
        "arm holdings": "ARM",
        "arm": "ARM",
        "samsung electronics": "SSNLF",
        "samsung": "SSNLF",
        "lg electronics": "LGEIY",
        "lg": "LGEIY",
        "sony": "SONY",
        "panasonic": "PCRFY",
        "hitachi": "HTHIY",
        "toshiba": "TOSYY",
        "nxp semiconductors": "NXPI",
        "nxp": "NXPI",
        "stmicroelectronics": "STM",
        "renesas": "RNECY",
        "infineon": "IFNNY",
        "analog devices": "ADI",
        "marvell": "MRVL",
        "mediatek": "2454.TW",
        "xilinx": "AMD",  # Acquired by AMD
        "altera": "INTC",  # Acquired by Intel

        # Retail & Consumer
        "walmart": "WMT",
        "target": "TGT",
        "costco": "COST",
        "home depot": "HD",
        "lowe's": "LOW",
        "lowes": "LOW",
        "mcdonald's": "MCD",
        "mcdonalds": "MCD",
        "starbucks": "SBUX",
        "coca cola": "KO",
        "coca-cola": "KO",
        "coke": "KO",
        "pepsi": "PEP",
        "pepsico": "PEP",
        "nike": "NKE",
        "adidas": "ADDYY",
        "lululemon": "LULU",
        "chipotle": "CMG",
        "domino's": "DPZ",
        "dominos": "DPZ",
        "yum brands": "YUM",
        "kfc": "YUM",
        "taco bell": "YUM",
        "pizza hut": "YUM",
        "etsy": "ETSY",
        "ebay": "EBAY",
        "wayfair": "W",
        "dollar general": "DG",
        "dollar tree": "DLTR",
        "best buy": "BBY",
        "tj maxx": "TJX",
        "tjx": "TJX",

        # Finance
        "jpmorgan": "JPM",
        "jp morgan": "JPM",
        "bank of america": "BAC",
        "bofa": "BAC",
        "wells fargo": "WFC",
        "citigroup": "C",
        "citi": "C",
        "goldman sachs": "GS",
        "morgan stanley": "MS",
        "american express": "AXP",
        "amex": "AXP",
        "visa": "V",
        "mastercard": "MA",
        "blackrock": "BLK",
        "charles schwab": "SCHW",
        "schwab": "SCHW",
        "fidelity": "FNF",
        "berkshire hathaway": "BRK.A",
        "berkshire": "BRK.A",

        # Healthcare & Pharma
        "johnson & johnson": "JNJ",
        "johnson and johnson": "JNJ",
        "pfizer": "PFE",
        "merck": "MRK",
        "novartis": "NVS",
        "abbvie": "ABBV",
        "eli lilly": "LLY",
        "lilly": "LLY",
        "unitedhealth": "UNH",
        "united health": "UNH",
        "cvs": "CVS",
        "walgreens": "WBA",
        "moderna": "MRNA",
        "gilead": "GILD",
        "regeneron": "REGN",
        "amgen": "AMGN",
        "thermo fisher": "TMO",
        "abbott": "ABT",
        "abbott laboratories": "ABT",
        "medtronic": "MDT",

        # Telecom & Media
        "at&t": "T",
        "att": "T",
        "verizon": "VZ",
        "t-mobile": "TMUS",
        "tmobile": "TMUS",
        "comcast": "CMCSA",
        "charter": "CHTR",
        "disney": "DIS",
        "walt disney": "DIS",
        "warner bros discovery": "WBD",
        "warner": "WBD",
        "paramount": "PARA",
        "fox": "FOX",
        "netflix": "NFLX",

        # Automotive
        "ford": "F",
        "general motors": "GM",
        "gm": "GM",
        "toyota": "TM",
        "honda": "HMC",
        "bmw": "BMWYY",
        "mercedes": "MBGAF",
        "mercedes-benz": "MBGAF",
        "daimler": "MBGAF",
        "volkswagen": "VWAGY",
        "vw": "VWAGY",
        "ferrari": "RACE",
        "lucid": "LCID",
        "lucid motors": "LCID",
        "rivian": "RIVN",
        # Indian Companies
        "reliance industries": "RELIANCE.NS",
        "reliance": "RELIANCE.NS",
        "tata motors": "TATAMOTORS.NS",
        "tata steel": "TATASTEEL.NS",
        "hdfc bank": "HDB",
        "hdfc": "HDB",
        "icici bank": "IBN",
        "icici": "IBN",
        "state bank of india": "SBIN.NS",
        "sbi": "SBIN.NS",
        "axis bank": "AXISBANK.NS",
        "bajaj finance": "BAJFINANCE.NS",
        "bajaj": "BAJFINANCE.NS",
        "mahindra & mahindra": "M&M.NS",
        "mahindra": "M&M.NS",
        "larsen & toubro": "LT.NS",
        "l&t": "LT.NS",
        "bharti airtel": "BHARTIARTL.NS",
        "airtel": "BHARTIARTL.NS",
        "adani enterprises": "ADANIENT.NS",
        "adani": "ADANIENT.NS",
        "sun pharma": "SUNPHARMA.NS",
        "itc limited": "ITC.NS",
        "itc": "ITC.NS",
        "hindustan unilever": "HINDUNILVR.NS",
        "hul": "HINDUNILVR.NS",

        # Chinese Companies
        "china mobile": "CHL",
        "china telecom": "CHA",
        "china unicom": "CHU",
        "petrochina": "PTR",
        "sinopec": "SNP",
        "china construction bank": "CICHY",
        "industrial and commercial bank of china": "IDCBY",
        "icbc": "IDCBY",
        "bank of china": "BACHY",
        "agricultural bank of china": "ACGBY",
        "ping an insurance": "PNGAY",
        "ping an": "PNGAY",
        "china life insurance": "LFC",
        "huawei": "PRIVATE",
        "xiaomi": "XIACF",
        "oppo": "PRIVATE",
        "vivo": "PRIVATE",
        "byd": "BYDDY",
        "nio": "NIO",
        "li auto": "LI",
        "xpeng": "XPEV",
        "nikola": "NKLA",

        # Energy
        "exxon": "XOM",
        "exxonmobil": "XOM",
        "chevron": "CVX",
        "shell": "SHEL",
        "bp": "BP",
        "conocophillips": "COP",
        "occidental": "OXY",
        "oxy": "OXY",
        "halliburton": "HAL",
        "schlumberger": "SLB",
        "nextera energy": "NEE",
        "duke energy": "DUK",
        "southern company": "SO",

        # Industrial
        "boeing": "BA",
        "lockheed martin": "LMT",
        "lockheed": "LMT",
        "raytheon": "RTX",
        "rtx": "RTX",
        "general electric": "GE",
        "ge": "GE",
        "3m": "MMM",
        "caterpillar": "CAT",
        "honeywell": "HON",
        "ups": "UPS",
        "fedex": "FDX",
        "deere": "DE",
        "john deere": "DE",
        "northrop grumman": "NOC",
        "northrop": "NOC",
        "siemens": "SIEGY",

        # Travel & Hospitality
        "marriott": "MAR",
        "hilton": "HLT",
        "delta": "DAL",
        "delta air lines": "DAL",
        "united airlines": "UAL",
        "american airlines": "AAL",
        "southwest": "LUV",
        "southwest airlines": "LUV",
        "booking": "BKNG",
        "booking holdings": "BKNG",
        "expedia": "EXPE",
        "carnival": "CCL",
        "royal caribbean": "RCL"
    }

    key = company_name.lower().strip()
    if key in known:
        return known[key]

    try:
        params = {
            "function": "SYMBOL_SEARCH",
            "keywords": company_name,
            "apikey": API_KEY
        }
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "bestMatches" in data and len(data["bestMatches"]) > 0:
            # Return best match's symbol
            best_match = data["bestMatches"][0]
            return best_match.get("1. symbol")
        else:
            print(f"No symbol found for company name: {company_name}")
    except (requests.RequestException, ValueError) as e:
        print(f"Error fetching symbol for {company_name}: {e}")

    return None


def get_quarterly_financials(symbol: str) -> dict:
    params = {
        "function": "INCOME_STATEMENT",
        "symbol": symbol,
        "apikey": API_KEY
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        result = {}
        for report in data.get("quarterlyReports", []):
            date = report["fiscalDateEnding"]
            year, month = map(int, date.split("-")[:2])
            quarter = f"Q{(month - 1) // 3 + 1}"

            try:
                revenue = float(report.get("totalRevenue", 0) or 0)
                profit = float(report.get("netIncome", 0) or 0)
            except (ValueError, TypeError):
                continue

            result.setdefault(str(year), {})[quarter] = {
                "revenue": revenue,
                "profit": profit
            }

        return result

    except (requests.RequestException, ValueError) as e:
        print(f"Error fetching quarterly financials for {symbol}: {e}")
        return {}
