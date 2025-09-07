






import React from 'react';
import Head from 'next/head';

const Home: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      <Head>
        <title>Rover Operations Console</title>
        <meta name="description" content="Tele-operation and supervised autonomy platform for heavy machines" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto py-4 px-6 flex justify-between items-center">
          <h1 className="text-2xl font-semibold text-gray-900">Rover Operations</h1>
          <nav className="flex space-x-4">
            <a href="#" className="text-sm font-medium text-gray-500 hover:text-gray-700">Devices</a>
            <a href="#" className="text-sm font-medium text-gray-500 hover:text-gray-700">Sessions</a>
            <a href="#" className="text-sm font-medium text-gray-500 hover:text-gray-700">Settings</a>
          </nav>
        </div>
      </header>

      <main className="flex-grow max-w-7xl mx-auto py-8 px-6">
        <h2 className="text-xl font-semibold mb-4">Welcome to Rover Operations</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Device List */}
          <section className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium mb-4">Available Devices</h3>
            <div className="space-y-4">
              {[1, 2, 3].map(id => (
                <div key={id} className="flex items-center justify-between p-3 bg-gray-50 rounded-md hover:bg-gray-100 transition-colors">
                  <span className="text-sm font-medium">Hello Tractor {id}</span>
                  <button className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors">
                    Take Control
                  </button>
                </div>
              ))}
            </div>
          </section>

          {/* Video Feed Placeholder */}
          <section className="bg-white shadow rounded-lg p-6 col-span-1 md:col-span-2">
            <h3 className="text-lg font-medium mb-4">Live Video Feed</h3>
            <div className="aspect-w-16 aspect-h-9 bg-gray-200 rounded-md flex items-center justify-center text-gray-500">
              WebRTC video stream will appear here
            </div>
          </section>

          {/* Control Panel */}
          <section className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium mb-4">Control Panel</h3>
            <div className="space-y-4">
              <button className="w-full bg-red-600 text-white px-4 py-2 rounded-md font-semibold hover:bg-red-700 transition-colors">
                E-stop
              </button>

              <div className="flex items-center space-x-3">
                <label htmlFor="speed" className="text-sm font-medium">Speed:</label>
                <input type="range" id="speed" min="0" max="100" defaultValue="50" className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer" />
              </div>

              <button className="w-full bg-green-600 text-white px-4 py-2 rounded-md font-semibold hover:bg-green-700 transition-colors">
                Start Session Recording
              </button>
            </div>
          </section>
        </div>
      </main>

      <footer className="bg-white shadow-inner mt-auto py-6">
        <div className="max-w-7xl mx-auto px-6 text-center text-sm text-gray-500">
          © {new Date().getFullYear()} Rover Operations. All rights reserved.
        </div>
      </footer>
    </div>
  );
};

export default Home;






