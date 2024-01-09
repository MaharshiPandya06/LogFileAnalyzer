import React, { useState } from 'react';

function Filereader() {
  const [fileContent, setFileContent] = useState('');
  const [uploadedFile, setUploadedFile] = useState(null);

  const handleFileChange = (e) => {
    setUploadedFile(e.target.files[0]);
  };


  

  const handleUpload = () => {
    if (uploadedFile) {
      const reader = new FileReader();

      reader.onload = (event) => {
        const content = event.target.result;
        setFileContent(content);
        alert('File uploaded successfully!');
      };

      reader.readAsText(uploadedFile);
    } else {
      alert('Please select a file before uploading.');
    }
  };

  return (
    <div>
      <h1>File Reader</h1>
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleUpload}>Upload</button>


      {fileContent && (
        <div>
          <h2>File Content:</h2>
          <pre>{fileContent}</pre>
        </div>
      )}
    </div>
  );
}

export default Filereader;
