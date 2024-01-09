import React, { useState, useEffect } from 'react';
import TableComponent from './TableComponent';
import LineChart from './LineChartComponent';
import LogLevelSummary from './LogLevelFreq';

const Dashboard = () => {
  const [logs, setLogs] = useState([]);
  const [originalLogs, setOriginalLogs] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('http://localhost:5000/get_parsed_log_file_path');
        const data = await response.json();
        setOriginalLogs(data);
        setLogs(data);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, []);

  const updateLogs = (newLogs) => {
    setLogs(newLogs);
  };

  return (
    <div>
      <center><h1>Dashboard</h1></center>
      <TableComponent logs={logs} setLogs={updateLogs} originalLogs={originalLogs} />
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px', marginTop: '20px' }}>
        <LogLevelSummary logs={logs} logLevel="INFO" />
        <LogLevelSummary logs={logs} logLevel="WARNING" />
        <LogLevelSummary logs={logs} logLevel="ERROR" />
        <LogLevelSummary logs={logs} logLevel="DEBUG" />
      </div>
      <LineChart logs={logs} />
    </div>
  );
};

export default Dashboard;
