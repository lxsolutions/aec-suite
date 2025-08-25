import re
import json
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper
from models.land_listing import LandListing

class DDPropertyScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.ddproperty.com"
        self.search_url = f"{self.base_url}/land-for-sale/phuket"
    
    def scrape(self, max_pages=5):
        """Scrape land listings from DDproperty.com"""
        listings = []
        
        for page in range(1, max_pages + 1):
            url = f"{self.search_url}/p{page}"
            html = self.fetch_page(url)
            
            if not html:
                continue
            
            soup = BeautifulSoup(html, 'lxml')
            property_cards = soup.select('.ListingsListstyle__ListingListItemWrapper-srp__sc-i2mz0c-0')
            
            if not property_cards:
                break
            
            for card in property_cards:
                try:
                    # Extract data from the card
                    title_elem = card.select_one('h3.ListingCard__ListingCardTitle-srp__sc-1t5sb9r-6')
                    title = title_elem.text.strip() if title_elem else "No Title"
                    
                    link_elem = card.select_one('a.LinkOverlay-srp__sc-lfz0g3-0')
                    link = self.base_url + link_elem['href'] if link_elem and 'href' in link_elem.attrs else None
                    
                    location_elem = card.select_one('.ListingCard__ListingCardAddress-srp__sc-1t5sb9r-7')
                    location = location_elem.text.strip() if location_elem else "Phuket"
                    
                    price_elem = card.select_one('.PriceSection__Price-srp__sc-6imrxd-1')
                    price_text = price_elem.text.strip() if price_elem else "0"
                    price_thb = self._extract_price(price_text)
                    
                    size_elem = card.select_one('.ListingCard__ListingCardFeatures-srp__sc-1t5sb9r-8')
                    size_text = size_elem.text.strip() if size_elem else ""
                    size_sqm, size_rai = self._extract_size(size_text)
                    
                    # Get detailed page for more information
                    if link:
                        detail_html = self.fetch_page(link)
                        if detail_html:
                            detail_soup = BeautifulSoup(detail_html, 'lxml')
                            
                            description_elem = detail_soup.select_one('.section-description')
                            description = description_elem.text.strip() if description_elem else ""
                            
                            # Try to extract coordinates from script tags
                            lat, lng = self._extract_coordinates(detail_html)
                            
                            # Try to extract contact info
                            contact_elem = detail_soup.select_one('.agent-content')
                            contact_info = contact_elem.text.strip() if contact_elem else ""
                    else:
                        description = ""
                        lat, lng = None, None
                        contact_info = ""
                    
                    # Create a listing object
                    listing = LandListing(
                        title=title,
                        description=description,
                        location=location,
                        latitude=lat,
                        longitude=lng,
                        price_thb=price_thb,
                        price_usd=self.convert_thb_to_usd(price_thb),
                        size_sqm=size_sqm,
                        size_rai=size_rai,
                        contact_info=contact_info,
                        source_url=link,
                        source_website="ddproperty.com"
                    )
                    
                    listings.append(listing)
                except Exception as e:
                    print(f"Error processing listing: {e}")
                    continue
        
        return listings
    
    def _extract_price(self, price_text):
        """Extract price in THB from price text"""
        # Remove non-numeric characters and convert to float
        price_match = re.search(r'฿\s*([\d,.]+)', price_text)
        if price_match:
            price_str = price_match.group(1).replace(',', '')
            return float(price_str)
        return 0
    
    def _extract_size(self, size_text):
        """Extract size in square meters and rai from size text"""
        # Check for rai
        rai_match = re.search(r'([\d.]+)\s*rai', size_text, re.IGNORECASE)
        if rai_match:
            size_rai = float(rai_match.group(1))
            size_sqm = size_rai * 1600  # 1 rai = 1600 sqm
            return size_sqm, size_rai
        
        # Check for sqm
        sqm_match = re.search(r'([\d,]+)\s*sq[.\s]*m', size_text, re.IGNORECASE)
        if sqm_match:
            size_sqm = float(sqm_match.group(1).replace(',', ''))
            size_rai = size_sqm / 1600
            return size_sqm, size_rai
        
        return 0, 0
    
    def _extract_coordinates(self, html):
        """Extract latitude and longitude from the HTML"""
        # Look for coordinates in script tags
        try:
            # Try to find JSON data in script tags
            script_pattern = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', html, re.DOTALL)
            if script_pattern:
                json_data = json.loads(script_pattern.group(1))
                # Navigate through the JSON to find coordinates
                if 'propertyDetail' in json_data and 'location' in json_data['propertyDetail']:
                    location = json_data['propertyDetail']['location']
                    if 'latitude' in location and 'longitude' in location:
                        return float(location['latitude']), float(location['longitude'])
        except Exception as e:
            print(f"Error extracting coordinates: {e}")
        
        # Fallback to regex pattern matching
        lat_match = re.search(r'latitude["\']?\s*:\s*["\']?([\d.-]+)', html)
        lng_match = re.search(r'longitude["\']?\s*:\s*["\']?([\d.-]+)', html)
        
        lat = float(lat_match.group(1)) if lat_match else None
        lng = float(lng_match.group(1)) if lng_match else None
        
        return lat, lng