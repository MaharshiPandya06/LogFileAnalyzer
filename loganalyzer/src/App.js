import React, { useState, useRef } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';

/**
 * Main component for the Log File Analyzer web app.
 */
function App() {
  const [file, setFile] = useState(null);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [selectedFileName, setSelectedFileName] = useState('');
  const fileInputRef = useRef(null);
  const [isUploaded, setIsUploaded] = useState(false);

  /**
   * Handles the change event, that is, checks the size of the uploaded file.
   * @param {Object} e - The change event.
   */
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    // Check if the uploaded file is less than or equal to 10 MB.
    if (selectedFile && selectedFile.size > 10 * 1024 * 1024) {
      alert('File size exceeds the limit of 10 MB. Please select a smaller file.');
      return;
    }

    setFile(selectedFile);
    setSelectedFileName(selectedFile ? selectedFile.name : '');
  };

  /**
   * Handles the file, stores the input file to formData and calls the /upload
   * API.
   */
  const handleUpload = async () => {
    if (!file) {
      alert('Please select a file');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        alert(result.message);
        setFile(null); // Clear the selected file after successful upload
        setSelectedFileName(''); // Clear the selected file name
        setIsUploaded(true);
      } else {
        alert(`Error: ${result.error}. Only .log and .json files are supported.`);
      }
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  /**
   * Navigates back to the initial state before file upload.
   */
  const handleBack = () => {
    setIsUploaded(false);
    setFile(null);
  }

  return (
    <div className="App">
      {!isUploaded && (
        <>
        <center>
      <h1 className='heading'> Log File Analyzer </h1>
      <label htmlFor="file-input" className="dropbox-label">
        <img src="/R.png" alt="Dropbox Logo" />
        {file ? (
          <span> {file.name}</span>
        ) : (
          <span>Choose File</span>
        )}
      </label>
      <input
        id="file-input"
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        style={{ display: 'none' }}
      />
      </center>
      </>
      )}

      {file && (
        <center>
        <div >
          <button onClick={handleUpload} className="selected-file-box">Upload</button>
        </div>
        </center>
      )}


      {uploadedFiles.length > 0 && (
        <div>
          <h2>Uploaded Files:</h2>
          <ul>
            {uploadedFiles.map((uploadedFile, index) => (
              <li key={index}>
                <a href={`http://localhost:5000/uploads/${uploadedFile}`} target="_blank" rel="noopener noreferrer">
                  {uploadedFile}
                </a>
              </li>
            ))}
          </ul>
        </div>

      )}

      {/* Table of log files */}
      {isUploaded && (
        <div>
        <button onClick={handleBack}>Back</button>
          <Dashboard/>
          
        </div>

      )}
    </div>
  );
}

export default App;
