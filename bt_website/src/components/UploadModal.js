// src/components/UploadModal.js
import React, { useState, useRef } from 'react';
import { FaUpload, FaTimes } from 'react-icons/fa';

export default function UploadModal({ isOpen, onClose, onFileUpload }) {
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null); // 🔑 Create a ref to the file input

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      onFileUpload(e.target.files[0]);
    }
  };

  // 🔑 Trigger file input when "Browse Files" is clicked
  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div 
        className={`upload-modal ${dragActive ? 'drag-active' : ''}`}
        onClick={(e) => e.stopPropagation()}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <button className="close-btn" onClick={onClose}>
          <FaTimes />
        </button>
        <div className="upload-content">
          <FaUpload className="upload-icon" />
          <h3>Upload MRI Scan</h3>
          <p>Drag & drop or click to browse</p>
          
          {/* 🔑 Hidden file input with ref */}
          <input
            type="file"
            accept=".jpg,.jpeg,.png"
            onChange={handleFileInput}
            ref={fileInputRef}  // ← Link the ref
            style={{ display: 'none' }}
          />
          
          {/* 🔑 Button that triggers the file input */}
          <button className="browse-btn" onClick={triggerFileInput}>
            Browse Files
          </button>
        </div>
      </div>
    </div>
  );
}