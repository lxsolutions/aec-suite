



import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  root: './', // Set the root directory
  publicDir: 'public', // Public directory for static assets
  build: {
    outDir: 'dist',
    rollupOptions: {
      input: 'public/index.html'
    }
  },
  server: {
    host: true, // Allow access from any host
    port: 3000,
    open: false, // Don't automatically open browser
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
});

