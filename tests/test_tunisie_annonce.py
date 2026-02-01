from scrapers.tunisie_annonce import TunisieAnnonceScraper

URL = "http://www.tunisie-annonce.com/AnnonceImmobilier.asp?..."

scraper = TunisieAnnonceScraper(URL)
data = scraper.scrape()

print(data)

assert "price" in data
assert "surface_area" in data
