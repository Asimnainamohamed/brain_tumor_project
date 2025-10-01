// src/components/Home.js
import React from 'react';
import { FaUpload } from 'react-icons/fa';

export default function Home({ onTryClick }) {
  return (
    <div className="home">
      <div className="hero">
        <h1>AI-Powered Brain Tumor Detection</h1>
        <p>Upload an MRI scan for instant, accurate diagnosis</p>
        <button className="try-btn" onClick={onTryClick}>
          <FaUpload /> Try Me
        </button>
        
      </div>
    </div>
  );
}