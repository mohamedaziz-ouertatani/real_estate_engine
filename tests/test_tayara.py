from scrapers.tayara import TayaraScraper

URL = "https://www.tayara.tn/item/..."

scraper = TayaraScraper(URL)
data = scraper.scrape()

print(data)
