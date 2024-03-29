import React, { useEffect, useState } from 'react';
import './TableComponent.css';

/**
 * Table component that shows all the logs in the following columns:
 * - Timestamp
 * - Log Level
 * - Log message
 */
const TableComponent = ({ logs, setLogs, originalLogs }) => {
  const [startTimestamp, setStartTimestamp] = useState('');
  const [endTimestamp, setEndTimestamp] = useState('');
  const [selectedLogLevel, setSelectedLogLevel] = useState(''); // Default to an empty string for showing all log levels

  useEffect(() => {
    // Sort original logs based on timestamp before setting in state
    const sortedOriginalLogs = originalLogs.slice().sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    
    console.log("helllo");
    setLogs(sortedOriginalLogs);
  }, []);

  /**
   * Handles the event of search button getting clicked.
   */
  const handleSearch = () => {
    // Filter logs based on the timestamp range
    const filteredLogs = originalLogs.filter(log => {
      const logTimestamp = new Date(log.timestamp).getTime();
      const startTimestampMillis = new Date(startTimestamp).getTime();
      const endTimestampMillis = new Date(endTimestamp).getTime();
      
      const isWithinTimestampRange =
      (!startTimestamp || logTimestamp >= startTimestampMillis) &&
      (!endTimestamp || logTimestamp <= endTimestampMillis)

      const isMatchingLogLevel = !selectedLogLevel || (log.log_level && log.log_level.toLowerCase()) === selectedLogLevel.toLowerCase() || (selectedLogLevel === 'WARNING' && log.log_level === 'WARN');
      
      return isWithinTimestampRange && isMatchingLogLevel;
    });

    // Sort filtered logs based on timestamp before updating the state
    const sortedFilteredLogs = filteredLogs.slice().sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    // Update the state with the filtered logs
    setLogs(sortedFilteredLogs);
  };

  /**
   * Handles the clear filter button click event.
   */
  const handleClearFilter = () => {
    // Clear filter values and reset logs to the original state
    setStartTimestamp('');
    setEndTimestamp('');
    setSelectedLogLevel('');
    setLogs(originalLogs);
  };

  const handleDownload = async () => {
    // Assuming you have the server URL where the Flask app is running
    const serverURL = 'http://localhost:5000/generate_pdf';

    // Sending a POST request to the Flask server
    const response = await fetch(serverURL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        start_timestamp: startTimestamp,
        end_timestamp: endTimestamp,
      }),
    });

    // Check if the request was successful
    if (response.ok) {
      // Convert the response to a Blob
      const blob = await response.blob();

      // Create a URL for the Blob
      const url = URL.createObjectURL(blob);

      // Create a download link
      const link = document.createElement('a');
      link.href = url;
      link.download = 'logs_report.pdf';

      // Trigger a click on the link to start the download
      link.click();

      // Clean up the URL created for the Blob
      URL.revokeObjectURL(url);
    } else {
      console.error('Error generating PDF:', response.statusText);
    }
  };

  return (
    <>
    {console.log("---------------------" + originalLogs[originalLogs.length-1])}
      <div className='search-bar'>
          <label>Start Timestamp:</label>
          <input type="datetime-local" value={startTimestamp} onChange={(e) => setStartTimestamp(e.target.value)} />
        
          <label>End Timestamp:</label>
          <input type="datetime-local" value={endTimestamp} onChange={(e) => setEndTimestamp(e.target.value)} />

          <label>Log Level:</label>
          <select value={selectedLogLevel} onChange={(e) => setSelectedLogLevel(e.target.value)}>
            <option value="">All</option>
            <option value="INFO">INFO</option>
            <option value="DEBUG">DEBUG</option>
            <option value="WARNING">WARNING</option>
            <option value="ERROR">ERROR</option>
          </select> 
      </div>

      <div className='filter-buttons'>
        <button onClick={handleSearch} className='search-button'>Search</button>
        <button onClick={handleClearFilter} className='clear-filter-button'>Clear Filter</button>
        <button onClick={handleDownload} className='download-button'>Download PDF</button>
      </div>
      <div className="table-container">
        <table className='log-table'>
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Log Level</th>
              <th>Message</th>
            </tr>
          </thead>
          <tbody>
            {logs.length > 0 ? logs.map((log, index) => (
              <tr key={index}>
                <td>{log.timestamp}</td>
                <td>{log.log_level}</td>
                <td>{log.message}</td>
              </tr>
            )) : <p>No logs available.</p>}
          </tbody>
        </table>
      </div>
    </>
  );
};

export default TableComponent;