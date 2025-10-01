// src/components/Header.js
import React from 'react';
import { FaHome, FaInfoCircle } from 'react-icons/fa';

export default function Header({ activePage, setActivePage }) {
  return (
    <header className="header">
      <div className="logo">🧠 BrainAI</div>
       <ul class="nav-links">
                <li><a href="#models">Models</a></li>
                <li><a href="#research">Research</a></li>
                <li><a href="#science">Science</a></li>
                <li><a href="#about">About</a></li>
            </ul>
     
    

      <nav>
        <button 
          className={activePage === 'home' ? 'active' : ''} 
          onClick={() => setActivePage('home')}
        >
          <FaHome /> Home
        </button>
        <button 
          className={activePage === 'about' ? 'active' : ''} 
          onClick={() => setActivePage('about')}
        >
          <FaInfoCircle /> About
        </button>
      </nav>
    </header>
  );
}