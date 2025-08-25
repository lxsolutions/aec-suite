from .thailand_property_scraper import ThailandPropertyScraper
from .ddproperty_scraper import DDPropertyScraper
from models import get_db_session
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_all_scrapers():
    """Run all scrapers and save results to database"""
    scrapers = [
        ThailandPropertyScraper(),
        DDPropertyScraper()
    ]
    
    db_session = get_db_session()
    total_listings = 0
    
    try:
        for scraper in scrapers:
            logger.info(f"Running scraper for {scraper.__class__.__name__}")
            listings = scraper.scrape()
            
            for listing in listings:
                # Check if listing already exists by source_url
                existing = db_session.query(listing.__class__).filter_by(source_url=listing.source_url).first()
                
                if existing:
                    # Update existing listing
                    for key, value in listing.__dict__.items():
                        if key != '_sa_instance_state' and key != 'id' and value is not None:
                            setattr(existing, key, value)
                else:
                    # Add new listing
                    db_session.add(listing)
                    total_listings += 1
            
            db_session.commit()
            logger.info(f"Completed scraper for {scraper.__class__.__name__}, processed {len(listings)} listings")
        
        logger.info(f"All scrapers completed. Added {total_listings} new listings.")
    except Exception as e:
        db_session.rollback()
        logger.error(f"Error running scrapers: {e}")
    finally:
        db_session.close()
    
    return total_listings