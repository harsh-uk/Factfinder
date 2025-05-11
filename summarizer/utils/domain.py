from urllib.parse import urlparse

def extract_domain(url: str):
    try:
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'
        return urlparse(url).netloc.lower()
    except Exception:
        return None