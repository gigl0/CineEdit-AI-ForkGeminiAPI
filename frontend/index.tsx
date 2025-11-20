// frontend/index.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App'; // Assicurati che sia ./App e non ./src/App
import './index.css';    // IMPORTANTE: Carica gli stili

const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error("Impossibile trovare l'elemento root");
}

const root = ReactDOM.createRoot(rootElement);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);