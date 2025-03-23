# Phuket Land Finder

A web application designed to help developers and buyers find land for sale in Phuket, Thailand. The app scrapes real estate websites for up-to-date land listings and presents them on an interactive map.

## Features

- **Web Scraping**: Automatically collects land listings from Thailand-property.com and DDproperty.com
- **Interactive Map**: Visualize land listings on a map of Phuket using Leaflet.js
- **Filtering**: Filter listings by price range, size, and location
- **Bilingual Support**: Toggle between English and Thai languages
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

### Backend
- Python
- Flask
- SQLAlchemy
- BeautifulSoup4
- APScheduler

### Frontend
- React
- Leaflet.js
- Tailwind CSS
- React Router

## Project Structure

```
phuket-land-finder/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   └── api.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── land_listing.py
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── base_scraper.py
│   │   ├── thailand_property_scraper.py
│   │   └── ddproperty_scraper.py
│   ├── static/
│   ├── templates/
│   ├── app.py
│   └── requirements.txt
└── frontend/
    ├── public/
    │   ├── index.html
    │   └── manifest.json
    ├── src/
    │   ├── components/
    │   │   ├── FilterPanel.js
    │   │   ├── Header.js
    │   │   ├── ListingCard.js
    │   │   └── Map.js
    │   ├── pages/
    │   │   ├── HomePage.js
    │   │   └── ListingDetailPage.js
    │   ├── utils/
    │   │   ├── api.js
    │   │   ├── LanguageContext.js
    │   │   └── translations.json
    │   ├── App.js
    │   └── index.js
    ├── package.json
    ├── tailwind.config.js
    └── postcss.config.js
```

## Setup and Installation

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd phuket-land-finder/backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the Flask application:
   ```
   python app.py
   ```

   The backend will be available at http://localhost:50560

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd phuket-land-finder/frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Run the React application:
   ```
   npm start
   ```

   The frontend will be available at http://localhost:56847

## Deployment

### Backend Deployment (Heroku)

1. Create a Procfile in the backend directory:
   ```
   web: gunicorn app:app
   ```

2. Deploy to Heroku:
   ```
   heroku create phuket-land-finder-api
   git push heroku main
   ```

### Frontend Deployment (Vercel)

1. Install Vercel CLI:
   ```
   npm install -g vercel
   ```

2. Deploy to Vercel:
   ```
   vercel
   ```

## Environment Variables

Create a `.env` file in the backend directory with the following variables:

```
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///land_listings.db
```

For production, you may want to use a different database like PostgreSQL.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [OpenStreetMap](https://www.openstreetmap.org/) for providing map data
- [Leaflet.js](https://leafletjs.com/) for the interactive map functionality
- [Tailwind CSS](https://tailwindcss.com/) for the UI components