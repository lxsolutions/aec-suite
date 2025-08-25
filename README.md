

# EstateJoint

A global real estate platform designed to help developers, buyers, and investors find land for sale worldwide. The app scrapes real estate websites for up-to-date listings and presents them on an interactive world map.

## Features

- **Global Land Finder**: Search land listings from around the world
- **Web Scraping**: Automatically collects listings from multiple real estate websites
- **Interactive World Map**: Visualize listings using Leaflet.js with clustering and filters
- **Advanced Filtering**: Filter by price range, size, location, country, region
- **Bilingual Support**: Toggle between English and Thai languages (architecture ready for more)
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

### Backend
- Python 3.11+
- Flask
- SQLAlchemy + GeoAlchemy2 + PostGIS
- BeautifulSoup4/selectolax
- Celery with Redis
- Alembic for migrations

### Frontend
- React
- Leaflet.js
- Tailwind CSS
- Vite (for dev speed)
- i18next for internationalization

## Project Structure

```
estatejoint/
в”њв”Ђв”Ђ backend/  # Renamed to estatejoint_api/
в”‚   в”њв”Ђв”Ђ app/
в”‚   в”‚   в”њв”Ђв”Ђ __init__.py
в”‚   в”‚   в””в”Ђв”Ђ api.py
в”‚   в”њв”Ђв”Ђ models/
в”‚   в”‚   в”њв”Ђв”Ђ __init__.py
в”‚   в”‚   в””в”Ђв”Ђ land_listing.py  # Renamed to listing.py
в”‚   в”њв”Ђв”Ђ scrapers/
в”‚   в”‚   в”њв”Ђв”Ђ __init__.py
в”‚   в”‚   в”њв”Ђв”Ђ base_scraper.py  # Base interface for providers
в”‚   в”‚   в”њв”Ђв”Ђ thailand_property_provider.py  # Refactored as provider
в”‚   в”‚   в””в”Ђв”Ђ ddproperty_provider.py  # Refactored as provider
в”‚   в”њв”Ђв”Ђ static/
в”‚   в”њв”Ђв”Ђ templates/
в”‚   в”њв”Ђв”Ђ app.py
в”‚   в””в”Ђв”Ђ requirements.txt  # Replaced with pyproject.toml
в””в”Ђв”Ђ frontend/  # Moved to apps/web/
    в”њв”Ђв”Ђ public/
    в”‚   в”њв”Ђв”Ђ index.html
    в”‚   в””в”Ђв”Ђ manifest.json
    в”њв”Ђв”Ђ src/
    в”‚   в”њв”Ђв”Ђ components/
    в”‚   в”‚   в”њв”Ђв”Ђ FilterPanel.js
    в”‚   в”‚   в”њв”Ђв”Ђ Header.js
    в”‚   в”‚   в”њв”Ђв”Ђ ListingCard.js
    в”‚   в”‚   в””в”Ђв”Ђ Map.js
    в”‚   в”њв”Ђв”Ђ pages/
    в”‚   в”‚   в”њв”Ђв”Ђ HomePage.js
    в”‚   в”‚   в””в”Ђв”Ђ ListingDetailPage.js
    в”‚   в”њв”Ђв”Ђ utils/
    в”‚   в”‚   в”њв”Ђв”Ђ api.js
    в”‚   в”‚   в”њв”Ђв”Ђ LanguageContext.js  # Migrated to i18next
    в”‚   в”‚   в””в”Ђв”Ђ translations.json  # Migrated to i18next catalogs
    в”‚   в”њв”Ђв”Ђ App.js
    в”‚   в””в”Ђв”Ђ index.js
    в”њв”Ђв”Ђ package.json
    в”њв”Ђв”Ђ tailwind.config.js
    в””в”Ђв”Ђ postcss.config.js
```

## Setup and Installation

### Prerequisites
- Docker 20+
- Python 3.11+
- Node.js 18+

### Development Environment with Docker

1. **Clone the repository:**
   ```bash
   git clone https://github.com/lxsolutions/estatejoint.git
   cd estatejoint
   ```

2. **Copy environment template and configure:**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

3. **Start the development environment:**
   ```bash
   docker-compose up --build
   ```
   This will start:
   - PostGIS database (port 5432)
   - Redis for task queue (port 6379)
   - Flask API backend (port 8000)
   - React frontend (port 3000)

### Manual Setup

#### Backend
1. **Navigate to the backend directory:**
   ```bash
   cd estatejoint/backend
   ```

2. **Set up virtual environment and install dependencies:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install --no-cache-dir poetry
   poetry install
   ```

3. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

4. **Start the Flask application:**
   ```bash
   flask run
   ```
   The backend will be available at http://localhost:5000

#### Frontend
1. **Navigate to the frontend directory:**
   ```bash
   cd estatejoint/frontend
   ```

2. **Install dependencies and start development server:**
   ```bash
   npm install
   npm run dev
   ```
   The frontend will be available at http://localhost:3000

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
# Database configuration
DB_HOST=postgres
DB_PORT=5432
DB_NAME=estatejoint
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_SCHEMA=public

# Redis for Celery
REDIS_URL=redis://redis:6379/0

# Flask and JWT configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=another-secret-key

# API configuration
API_HOST=http://localhost:5000
```

## Docker Compose Services

The `docker-compose.yml` file defines the following services:

- **api**: Flask backend with Gunicorn
- **web**: React frontend with Vite development server
- **db**: PostGIS-enabled PostgreSQL database
- **redis**: Redis for Celery task queue
- **worker**: Celery worker for background tasks

## API Documentation

The API follows RESTful principles and is versioned under `/v1/`. Available endpoints:

- `GET /v1/listings`: Search listings with filters (bbox, country, price range, etc.)
- `GET /v1/listings/{id}`: Get listing details
- `POST /v1/searches`: Save search queries for alerts

## Roadmap

### Phase 2 - Design Studio (Coming Soon)
- **Design Projects**: Create and manage design projects tied to listings
- **House Plans**: Browse preset plans with attributes (bed/bath, footprint)

### Phase 3 - Vendor Network
- **Vendor Directory**: Find architects, contractors, surveyors

### Phase 4 - Co-Investment Platform
- **Project Crowdfunding**: Invest in real estate projects collaboratively

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [OpenStreetMap](https://www.openstreetmap.org/) for providing map data
- [Leaflet.js](https://leafletjs.com/) for the interactive map functionality
- [Tailwind CSS](https://tailwindcss.com/) for the UI components
