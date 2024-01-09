import React, { useEffect, useState } from 'react';
import './TableComponent.css';

const TableComponent = ({ logs, setLogs, originalLogs }) => {
  const [startTimestamp, setStartTimestamp] = useState('');
  const [endTimestamp, setEndTimestamp] = useState('');
  const [selectedLogLevel, setSelectedLogLevel] = useState(''); // Default to an empty string for showing all log levels

  useEffect(() => {
    // Sort original logs based on timestamp before setting in state
    const sortedOriginalLogs = originalLogs.slice().sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    setLogs(sortedOriginalLogs);
  }, []);

  const handleSearch = () => {
    // Filter logs based on the timestamp range
    const filteredLogs = originalLogs.filter(log => {
      const logTimestamp = new Date(log.timestamp).getTime();
      const startTimestampMillis = new Date(startTimestamp).getTime();
      const endTimestampMillis = new Date(endTimestamp).getTime();

      const isWithinTimestampRange =
      !startTimestamp || !endTimestamp ||
      (logTimestamp >= startTimestampMillis && logTimestamp <= endTimestampMillis);

      const isMatchingLogLevel = !selectedLogLevel || (log.log_level && log.log_level.toLowerCase()) === selectedLogLevel.toLowerCase() || (selectedLogLevel === 'WARNING' && log.log_level === 'WARN');
      
      return isWithinTimestampRange && isMatchingLogLevel;
    });

    // Sort filtered logs based on timestamp before updating the state
    const sortedFilteredLogs = filteredLogs.slice().sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    console.log(sortedFilteredLogs)
    // Update the state with the filtered logs
    setLogs(sortedFilteredLogs);
  };

  const handleClearFilter = () => {
    // Clear filter values and reset logs to the original state
    setStartTimestamp('');
    setEndTimestamp('');
    setSelectedLogLevel('');
    setLogs(originalLogs);
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

      <div className='filter-buttons'>
        <button onClick={handleSearch} className='search-button'>Search</button>
        <button onClick={handleClearFilter} className='clear-filter-button'>Clear Filter</button>
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