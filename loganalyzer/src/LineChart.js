import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';

const LineChart = ({ logs }) => {
  const [chartData, setChartData] = useState(null);

  useEffect(() => {
    const sortedLogs = logs.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

    const labels = sortedLogs.map(log => log.timestamp);
    const datasets = [
      {
        label: 'Log Level',
        data: sortedLogs.map(log => ({
          x: new Date(log.timestamp),
          y: logLevelToNumber(log.log_level),
        })),
        borderColor: 'blue',
        fill: false,
      },
    ];

    const data = {
      labels,
      datasets,
    };

    setChartData(data);
  }, [logs]);

  const logLevelToNumber = logLevel => {
    switch (logLevel) {
      case 'INFO':
        return 1;
      case 'DEBUG':
        return 2;
      case 'WARNING':
        return 3;
      case 'ERROR':
        return 4;
      default:
        return 0;
    }
  };

  const options = {
    scales: {
      x: {
        type: 'time',
        position: 'bottom',
        title: {
          display: true,
          text: 'Timestamp',
        },
      },
      y: {
        type: 'linear',
        position: 'left',
        title: {
          display: true,
          text: 'Log Level',
        },
        ticks: {
          stepSize: 1,
          min: 0,
          max: 5,
          callback: value => {
            switch (value) {
              case 1:
                return 'INFO';
              case 2:
                return 'DEBUG';
              case 3:
                return 'WARNING';
              case 4:
                return 'ERROR';
              default:
                return '';
            }
          },
        },
      },
    },
  };

  return (
    <div>
      {chartData && <Line data={chartData} options={options} />}
    </div>
  );
};

export default LineChart;
