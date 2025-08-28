import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from models import init_db, get_db_session
from models.land_listing import LandListing, Base
from datetime import datetime
from sqlalchemy import create_engine

def create_sample_data():
    """Create sample data for testing"""
    # Create database and tables
    engine = create_engine('sqlite:///land_listings.db')
    Base.metadata.create_all(engine)
    
    init_db()
    db_session = get_db_session()
    
    # Check if we already have data
    existing_count = db_session.query(LandListing).count()
    if existing_count > 0:
        print(f"Database already contains {existing_count} listings. Skipping sample data creation.")
        return
    
    # Sample data
    sample_listings = [
        {
            "title": "Beautiful Land Plot in Patong",
            "description": "A beautiful land plot with sea view in Patong area. Perfect for villa development.",
            "location": "Patong, Phuket",
            "latitude": 7.8965,
            "longitude": 98.2963,
            "price_thb": 15000000,
            "price_usd": 420000,
            "size_sqm": 800,
            "size_rai": 0.5,
            "contact_info": "John Doe: +66 89 123 4567",
            "source_url": "https://example.com/listing1",
            "source_website": "thailand-property.com"
        },
        {
            "title": "Large Land Plot in Rawai",
            "description": "Large land plot suitable for resort development in Rawai area.",
            "location": "Rawai, Phuket",
            "latitude": 7.7767,
            "longitude": 98.3233,
            "price_thb": 25000000,
            "price_usd": 700000,
            "size_sqm": 1600,
            "size_rai": 1,
            "contact_info": "Jane Smith: +66 81 987 6543",
            "source_url": "https://example.com/listing2",
            "source_website": "ddproperty.com"
        },
        {
            "title": "Beachfront Land in Kamala",
            "description": "Rare beachfront land opportunity in Kamala. Perfect for luxury villa or small resort.",
            "location": "Kamala, Phuket",
            "latitude": 7.9566,
            "longitude": 98.2833,
            "price_thb": 50000000,
            "price_usd": 1400000,
            "size_sqm": 1200,
            "size_rai": 0.75,
            "contact_info": "Property Expert Co.: +66 76 123 4567",
            "source_url": "https://example.com/listing3",
            "source_website": "thailand-property.com"
        },
        {
            "title": "Development Land in Chalong",
            "description": "Large land plot ideal for housing development in Chalong area.",
            "location": "Chalong, Phuket",
            "latitude": 7.8484,
            "longitude": 98.3307,
            "price_thb": 32000000,
            "price_usd": 896000,
            "size_sqm": 3200,
            "size_rai": 2,
            "contact_info": "Developer Agency: +66 89 555 7777",
            "source_url": "https://example.com/listing4",
            "source_website": "ddproperty.com"
        },
        {
            "title": "Mountain View Land in Kata",
            "description": "Beautiful land with mountain views in Kata area. Short drive to the beach.",
            "location": "Kata, Phuket",
            "latitude": 7.8208,
            "longitude": 98.3036,
            "price_thb": 18000000,
            "price_usd": 504000,
            "size_sqm": 960,
            "size_rai": 0.6,
            "contact_info": "Phuket Land Expert: +66 81 234 5678",
            "source_url": "https://example.com/listing5",
            "source_website": "thailand-property.com"
        },
        {
            "title": "Investment Land in Bang Tao",
            "description": "Prime investment land in Bang Tao area near luxury resorts.",
            "location": "Bang Tao, Phuket",
            "latitude": 8.0023,
            "longitude": 98.2977,
            "price_thb": 28000000,
            "price_usd": 784000,
            "size_sqm": 1920,
            "size_rai": 1.2,
            "contact_info": "Investment Property Co.: +66 76 987 6543",
            "source_url": "https://example.com/listing6",
            "source_website": "ddproperty.com"
        },
        {
            "title": "Sea View Land in Karon",
            "description": "Stunning sea view land in Karon. Perfect for luxury villa development.",
            "location": "Karon, Phuket",
            "latitude": 7.8536,
            "longitude": 98.2964,
            "price_thb": 35000000,
            "price_usd": 980000,
            "size_sqm": 1600,
            "size_rai": 1,
            "contact_info": "Luxury Property Phuket: +66 89 876 5432",
            "source_url": "https://example.com/listing7",
            "source_website": "thailand-property.com"
        },
        {
            "title": "Commercial Land in Phuket Town",
            "description": "Commercial land plot in Phuket Town. Ideal for retail or office development.",
            "location": "Phuket Town, Phuket",
            "latitude": 7.8804,
            "longitude": 98.3923,
            "price_thb": 40000000,
            "price_usd": 1120000,
            "size_sqm": 2400,
            "size_rai": 1.5,
            "contact_info": "Commercial Property Agency: +66 76 345 6789",
            "source_url": "https://example.com/listing8",
            "source_website": "ddproperty.com"
        },
        {
            "title": "Hillside Land in Surin",
            "description": "Beautiful hillside land in Surin with partial sea views.",
            "location": "Surin, Phuket",
            "latitude": 7.9756,
            "longitude": 98.2789,
            "price_thb": 22000000,
            "price_usd": 616000,
            "size_sqm": 1280,
            "size_rai": 0.8,
            "contact_info": "Phuket Land Sales: +66 81 111 2222",
            "source_url": "https://example.com/listing9",
            "source_website": "thailand-property.com"
        },
        {
            "title": "Agricultural Land in Thalang",
            "description": "Large agricultural land in Thalang area. Good investment opportunity.",
            "location": "Thalang, Phuket",
            "latitude": 8.0249,
            "longitude": 98.3444,
            "price_thb": 12000000,
            "price_usd": 336000,
            "size_sqm": 4800,
            "size_rai": 3,
            "contact_info": "Land Investment Co.: +66 89 333 4444",
            "source_url": "https://example.com/listing10",
            "source_website": "ddproperty.com"
        }
    ]
    
    # Create and add listings
    for data in sample_listings:
        listing = LandListing(
            title=data["title"],
            description=data["description"],
            location=data["location"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            price_thb=data["price_thb"],
            price_usd=data["price_usd"],
            size_sqm=data["size_sqm"],
            size_rai=data["size_rai"],
            contact_info=data["contact_info"],
            source_url=data["source_url"],
            source_website=data["source_website"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(listing)
    
    db_session.commit()
    print(f"Added {len(sample_listings)} sample listings to the database.")

if __name__ == "__main__":
    create_sample_data()