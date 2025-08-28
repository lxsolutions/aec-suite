from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class LandListing(Base):
    __tablename__ = 'land_listings'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    price_thb = Column(Float, nullable=False)
    price_usd = Column(Float, nullable=True)
    size_sqm = Column(Float, nullable=False)
    size_rai = Column(Float, nullable=True)
    contact_info = Column(String(255), nullable=True)
    source_url = Column(String(512), nullable=False)
    source_website = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'price_thb': self.price_thb,
            'price_usd': self.price_usd,
            'size_sqm': self.size_sqm,
            'size_rai': self.size_rai,
            'contact_info': self.contact_info,
            'source_url': self.source_url,
            'source_website': self.source_website,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }