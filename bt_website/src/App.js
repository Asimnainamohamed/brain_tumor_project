import React, { useState } from 'react';
import Header from './components/Header';
import Home from './components/Home';
import About from './components/About';
import UploadModal from './components/UploadModal';
import './App.css';



function App() {
  const [activePage, setActivePage] = useState('home');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [error, setError] = useState('');

  const handleTryClick = () => setIsModalOpen(true);
  const closeModal = () => {
    setIsModalOpen(false);
    setError('');
  };

  const handleFileUpload = async (file) => {
    // Validate file
    if (!['image/jpeg', 'image/png'].includes(file.type)) {
      setError('Please upload a JPG or PNG image');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://127.0.0.1:5000/predict', {
        method: 'POST',
        body: formData,
      });
      const result = await response.json();
      
      if (response.ok) {
        setPrediction(result);
        setIsModalOpen(false);        // 👈 Close modal
        setActivePage('result');      // 👈 Switch to result page
    } 
       else {
        setError(result.error || 'Invalid MRI scan');
      }
    } catch (err) {
      setError('Failed to connect to AI server');
    }
  };

  return (
    <div className="App">
      <Header activePage={activePage} setActivePage={setActivePage} />
      
      {activePage === 'home' && <Home onTryClick={handleTryClick} />}
      {activePage === 'about' && <About />}
      {activePage === 'result' && (
        <div className="result-page">
          <h2>{prediction?.class}</h2>
          <p>Confidence: {prediction?.confidence}%</p>
          <button className="back-btn" onClick={() => setActivePage('home')}>
            ← Upload Another
          </button>
        </div>
      )}
      {isModalOpen &&(
      <UploadModal 
        isOpen={isModalOpen} 
        onClose={closeModal} 
        onFileUpload={handleFileUpload} 
      />  
      )}

      {error && (
        <div className="error-banner">
          {error}
          <button onClick={() => setError('')}>×</button>
        </div>
      )}
    </div>
  );
}

export default App;