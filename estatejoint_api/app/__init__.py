from flask import Flask
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__, 
                static_folder='../static', 
                template_folder='../templates')
    
    # Enable CORS
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Load configuration
    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev'),
        DATABASE_URL=os.getenv('DATABASE_URL', 'sqlite:///land_listings.db'),
    )
    
    # Initialize database
    from models import init_db
    init_db()
    
    # Register blueprints
    from app.api import api_bp
    app.register_blueprint(api_bp)
    
    # Set up scheduler for scraping
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        scheduler = BackgroundScheduler()
        from scrapers import run_all_scrapers
        
        # Schedule the scraper to run daily at midnight
        scheduler.add_job(run_all_scrapers, 'cron', hour=0, minute=0)
        
        # Also run once at startup
        scheduler.add_job(run_all_scrapers, 'date')
        
        scheduler.start()
        app.logger.info('Scheduler started')
    
    return app