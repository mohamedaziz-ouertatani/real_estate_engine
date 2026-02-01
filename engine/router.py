from urllib.parse import urlparse
from scrapers.tunisie_annonce import TunisieAnnonceScraper
from scrapers.tayara import TayaraScraper
from scrapers.facebook import FacebookMarketplaceScraper

def get_scraper(url: str):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()
    path = parsed_url.path.lower()

    if "tunisie-annonce.com" in domain:
        return TunisieAnnonceScraper(url)

    if "tayara.tn" in domain:
        return TayaraScraper(url)

    # FIX: Check domain and path separately to handle subdomains and tracking params
    if "facebook.com" in domain and "/marketplace" in path:
        return FacebookMarketplaceScraper(url)

    raise ValueError(f"Unsupported URL source: {domain}")