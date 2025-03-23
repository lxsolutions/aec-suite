import requests
import time
import random
from fake_useragent import UserAgent
from abc import ABC, abstractmethod

class BaseScraper(ABC):
    def __init__(self, delay_range=(1, 3)):
        self.delay_range = delay_range
        self.user_agent = UserAgent()
    
    def get_headers(self):
        return {
            'User-Agent': self.user_agent.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def fetch_page(self, url):
        """Fetch a page with random delay and rotating user agent"""
        # Random delay to avoid overloading the server
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)
        
        try:
            response = requests.get(url, headers=self.get_headers(), timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    @abstractmethod
    def scrape(self):
        """Implement this method in each scraper to extract land listings"""
        pass
    
    @staticmethod
    def convert_to_sqm(size, unit):
        """Convert various land size units to square meters"""
        unit = unit.lower()
        if unit == 'rai':
            return size * 1600  # 1 Rai = 1600 sqm
        elif unit == 'ngan':
            return size * 400   # 1 Ngan = 400 sqm
        elif unit == 'wah' or unit == 'sq wah' or unit == 'square wah':
            return size * 4     # 1 Square Wah = 4 sqm
        elif unit == 'sqm' or unit == 'sq m' or unit == 'square meter' or unit == 'square metre':
            return size
        else:
            return size  # Default to original size if unit is unknown
    
    @staticmethod
    def convert_thb_to_usd(thb_amount, exchange_rate=0.028):
        """Convert THB to USD using a fixed exchange rate (can be updated)"""
        return thb_amount * exchange_rate