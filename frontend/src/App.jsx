<<<<<<< Updated upstream
import { useState } from 'react'
import OCRPanel from './components/OCRPanel'
import './App.css'
=======
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { LanguageProvider } from './context/LanguageContext';

// Layout
import Layout from './components/Layout/Layout';

// Pages
import DashboardPage from './pages/DashboardPage';
import UploadPage from './pages/UploadPage';
import VerificationPage from './pages/VerificationPage';

import './App.css';
>>>>>>> Stashed changes

function App() {
  return (
<<<<<<< Updated upstream
    <main className="min-h-screen bg-slate-100 p-6">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-4xl font-bold mb-6">OCR with Django + Tesseract + React</h1>
        <OCRPanel />
        <section className="mt-8">
          <h2 className="text-2xl font-semibold">Demo counter</h2>
          <p className="my-3">Count is {count}</p>
          <button
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            onClick={() => setCount((n) => n + 1)}
          >
            Increment
          </button>
        </section>
      </div>
    </main>
  )
=======
    <LanguageProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<DashboardPage />} />
            <Route path="upload" element={<UploadPage />} />
            <Route path="verify" element={<VerificationPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </LanguageProvider>
  );
>>>>>>> Stashed changes
}

export default App;
