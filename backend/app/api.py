from flask import Blueprint, jsonify, request
from sqlalchemy import and_
from models import get_db_session
from models.land_listing import LandListing
import logging

api_bp = Blueprint('api', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)

@api_bp.route('/land', methods=['GET'])
def get_land_listings():
    """Get land listings with optional filters"""
    db_session = get_db_session()
    
    try:
        # Get filter parameters
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        min_size = request.args.get('min_size', type=float)
        max_size = request.args.get('max_size', type=float)
        location = request.args.get('location', type=str)
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Build query with filters
        query = db_session.query(LandListing)
        
        if min_price is not None:
            query = query.filter(LandListing.price_thb >= min_price)
        
        if max_price is not None:
            query = query.filter(LandListing.price_thb <= max_price)
        
        if min_size is not None:
            query = query.filter(LandListing.size_sqm >= min_size)
        
        if max_size is not None:
            query = query.filter(LandListing.size_sqm <= max_size)
        
        if location is not None:
            query = query.filter(LandListing.location.ilike(f'%{location}%'))
        
        # Get total count for pagination
        total_count = query.count()
        
        # Apply pagination
        query = query.order_by(LandListing.updated_at.desc())
        query = query.limit(limit).offset(offset)
        
        # Convert to dict
        listings = [listing.to_dict() for listing in query.all()]
        
        return jsonify({
            'listings': listings,
            'total': total_count,
            'limit': limit,
            'offset': offset
        })
    
    except Exception as e:
        logger.error(f"Error fetching land listings: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db_session.close()

@api_bp.route('/land/<int:listing_id>', methods=['GET'])
def get_land_listing(listing_id):
    """Get a specific land listing by ID"""
    db_session = get_db_session()
    
    try:
        listing = db_session.query(LandListing).filter(LandListing.id == listing_id).first()
        
        if not listing:
            return jsonify({'error': 'Listing not found'}), 404
        
        return jsonify(listing.to_dict())
    
    except Exception as e:
        logger.error(f"Error fetching land listing {listing_id}: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db_session.close()

@api_bp.route('/regions', methods=['GET'])
def get_regions():
    """Get all unique regions/locations in Phuket"""
    db_session = get_db_session()
    
    try:
        # Get distinct locations
        locations = db_session.query(LandListing.location).distinct().all()
        
        # Extract location names and clean them
        regions = []
        for loc in locations:
            # Split by commas and get the last part (usually the district/area)
            parts = loc[0].split(',')
            region = parts[-1].strip() if parts else loc[0]
            
            if region and region not in regions and 'phuket' in region.lower():
                regions.append(region)
        
        return jsonify(regions)
    
    except Exception as e:
        logger.error(f"Error fetching regions: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db_session.close()

@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get statistics about the land listings"""
    db_session = get_db_session()
    
    try:
        # Get total count
        total_count = db_session.query(LandListing).count()
        
        # Get price range
        min_price = db_session.query(LandListing.price_thb).order_by(LandListing.price_thb.asc()).first()
        max_price = db_session.query(LandListing.price_thb).order_by(LandListing.price_thb.desc()).first()
        
        # Get size range
        min_size = db_session.query(LandListing.size_sqm).order_by(LandListing.size_sqm.asc()).first()
        max_size = db_session.query(LandListing.size_sqm).order_by(LandListing.size_sqm.desc()).first()
        
        # Get latest update time
        latest_update = db_session.query(LandListing.updated_at).order_by(LandListing.updated_at.desc()).first()
        
        return jsonify({
            'total_listings': total_count,
            'price_range': {
                'min': min_price[0] if min_price else 0,
                'max': max_price[0] if max_price else 0
            },
            'size_range': {
                'min': min_size[0] if min_size else 0,
                'max': max_size[0] if max_size else 0
            },
            'latest_update': latest_update[0].isoformat() if latest_update else None
        })
    
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db_session.close()