import React from 'react';
import './LogLevelFreq.css'

/**
 * Log level frequency component that keeps track of the count
 * of log levels.
 */
const LogLevelFreq = ({ logs, logLevel }) => {
  // Filter logs based on the specified log level
  const filteredLogs = logs.filter(log => log.log_level === logLevel || (logLevel === 'WARNING' && log.log_level === 'WARN'));

  return (
    <div className='log-level-freq-card'>
      <h3>{logLevel}</h3>
      <p>Count: {filteredLogs.length}</p>
    </div>
  );
};

export default LogLevelFreq;
