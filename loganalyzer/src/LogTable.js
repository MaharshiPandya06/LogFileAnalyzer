import React, { useEffect, useState } from 'react';
import './LogTable.css';

const TableComponent = () => {
  const [originalLogs, setOriginalLogs] = useState([]);
  const [logs, setLogs] = useState([]);
  const [startTimestamp, setStartTimestamp] = useState('');
  const [endTimestamp, setEndTimestamp] = useState('');
  const [selectedLogLevel, setSelectedLogLevel] = useState(''); // Default to an empty string for showing all log levels

  useEffect(() => {
    // Fetch data from the JSON file (replace with your API call or data source)
    fetch('http://localhost:5000/get_parsed_log_file_path')
      .then(response => response.json())
      .then(data => {
        setOriginalLogs(data);
        setLogs(data);
      })
      .catch(error => console.error('Error fetching data:', error));
  }, []);

  const handleSearch = () => {
    // Filter logs based on the timestamp range
    const filteredLogs = originalLogs.filter(log => {
      const logTimestamp = new Date(log.timestamp).getTime();
      const startTimestampMillis = new Date(startTimestamp).getTime();
      const endTimestampMillis = new Date(endTimestamp).getTime();
      // console.log("start: " + startTimestamp);
      // console.log("end: " + endTimestamp);
      // console.log("log: " + logTimestamp);
      // console.log(selectedLogLevel);
      const isWithinTimestampRange =
      !startTimestamp || !endTimestamp ||
      (logTimestamp >= startTimestampMillis && logTimestamp <= endTimestampMillis);
      // console.log("selected:" + selectedLogLevel + " " + log.log_level)
      // const isMatchingLogLevel = !selectedLogLevel || log.logLevel === selectedLogLevel;
      const isMatchingLogLevel = !selectedLogLevel || (log.log_level && log.log_level.toLowerCase()) === selectedLogLevel.toLowerCase();
      
      return isWithinTimestampRange && isMatchingLogLevel;
      // return logTimestamp >= startTimestampMillis && logTimestamp <= endTimestampMillis;
    });
    // console.log("logs:" + logs.length);
    // console.log("temp_logs:" + temp_logs.length);

    // Update the state with the filtered logs
    setLogs(filteredLogs);
  };

  return (
    <>
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

      <div className='search-button'>
        <button onClick={handleSearch}>Search</button>
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