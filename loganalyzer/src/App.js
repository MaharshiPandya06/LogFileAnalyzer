import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import TableComponent from './LogTable';
import LineChart from './LineChart';
import Dashboard from './temp/Dashboard';
import html2pdf from 'html2pdf.js';

function App() {
  const [file, setFile] = useState(null);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [selectedFileName, setSelectedFileName] = useState('');
  const fileInputRef = useRef(null);
  const [isUploaded, setIsUploaded] = useState(false);
  const dashboardRef = useRef();

  useEffect(() => {
    // Fetch the list of uploaded files when the component mounts
    fetch('http://localhost:5000/get_uploaded_files')
      .then(response => response.json())
      .then(data => setUploadedFiles(data.files))
      .catch(error => console.error('Error fetching uploaded files:', error));
  }, []); // Empty dependency array to run the effect only once

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];

    if (selectedFile && selectedFile.size > 10 * 1024 * 1024) {
      alert('File size exceeds the limit of 10 MB. Please select a smaller file.');
      return;
    }

    setFile(selectedFile);
    setSelectedFileName(selectedFile ? selectedFile.name : '');
  };

  const handleDownload = () => {
    const content = dashboardRef.current;

    html2pdf(content, {
      margin: 10,
      filename: 'dashboard_report.pdf',
      image: { type: 'png', quality: 1 },
      html2canvas: { scale: 2 },
      jsPDF: { unit: 'mm', format: '', orientation: 'landscape' },
    });
  };

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
        setIsUploaded(true)
        // No need to fetch the updated list of uploaded files,
        // as the backend will now save the file in the "uploads" folder.

      } else {
        alert(`Error: ${result.error}`);
      }
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  const handleButtonClick = () => {
    fileInputRef.current.click();
  };


  return (
    <div className="App">
      {!isUploaded && (
        <>
      <h1 className='heading'> Log File Analyzer </h1>
      <label htmlFor="file-input" className="dropbox-label">
        <img src="/R.png" alt="Dropbox Logo" />
        {file ? (
          <span> {file.name}</span>
        ) : (
          <span>Drop File</span>
        )}
      </label>
      <input
        id="file-input"
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        style={{ display: 'none' }}
      />
      </>
      )}

      {file && (
        <div className="selected-file-box">
          <button onClick={handleUpload}>Upload</button>
        </div>
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
        <div ref={dashboardRef}>
          {/* <TableComponent />
          <div>
            <h1>Log Line Chart</h1>
            <LineChart logs={logs} />
          </div> */}
          <Dashboard/>
          <button onClick={handleDownload}>Download PDF</button>
        </div>

      )}
    </div>
  );
}

export default App;
