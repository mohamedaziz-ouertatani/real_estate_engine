from abc import ABC, abstractmethod

class BaseScraper(ABC):

    def __init__(self, url: str):
        self.url = url
        self.raw = {}

    @abstractmethod
    def fetch(self):
        pass

    @abstractmethod
    def parse(self):
        pass

    @abstractmethod
    def normalize(self) -> dict:
        pass

    def scrape(self) -> dict:
        self.fetch()
        self.parse()
        return self.normalize()
