import { useState, useEffect } from 'react';
import axios from 'axios';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import BidPlanBill from './components/BidPlanBill';

// Fix for default marker icon in react-leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

function App() {
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeView, setActiveView] = useState('land'); // 'land' or 'aec'

  useEffect(() => {
    if (activeView === 'land') {
      fetchListings();
    }
  }, [activeView]);

  const fetchListings = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:50981/api/land');
      setListings(response.data.listings);
      setError(null);
    } catch (err) {
      setError('Failed to fetch listings. Please try again later.');
      console.error('Error fetching listings:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4">
          <h1 className="text-3xl font-bold text-gray-900">EstateJoint Platform</h1>
          <div className="flex space-x-4 mt-4">
            <button
              onClick={() => setActiveView('land')}
              className={`px-4 py-2 rounded-md ${
                activeView === 'land' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Land Listings
            </button>
            <button
              onClick={() => setActiveView('aec')}
              className={`px-4 py-2 rounded-md ${
                activeView === 'aec' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              AEC Suite (Bid→Plan→Bill)
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 px-4">
        {error && (
          <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-6">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {activeView === 'aec' ? (
          <BidPlanBill />
        ) : (
          <>
            {loading ? (
              <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white shadow rounded-lg overflow-hidden">
                  <MapContainer
                    center={[7.9519, 98.3381]}
                    zoom={11}
                    className="h-[600px]"
                  >
                    <TileLayer
                      url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                      attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    />
                    {listings.map(listing => (
                      <Marker
                        key={listing.id}
                        position={[listing.latitude, listing.longitude]}
                      >
                        <Popup>
                          <div>
                            <h3 className="font-semibold">{listing.title}</h3>
                            <p>Price: THB {listing.price_thb.toLocaleString()}</p>
                            <p>Size: {listing.size_sqm} sqm</p>
                            <p>Location: {listing.location}</p>
                          </div>
                        </Popup>
                      </Marker>
                    ))}
                  </MapContainer>
                </div>

                <div className="space-y-4">
                  {listings.map(listing => (
                    <div key={listing.id} className="bg-white shadow rounded-lg p-4">
                      <h3 className="text-lg font-semibold">{listing.title}</h3>
                      <p className="mt-1 text-gray-500">{listing.description}</p>
                      <div className="mt-2">
                        <p>Price: THB {listing.price_thb.toLocaleString()}</p>
                        <p>Size: {listing.size_sqm} sqm ({listing.size_rai} rai)</p>
                        <p>Location: {listing.location}</p>
                        <p>Contact: {listing.contact_info}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}

export default App;