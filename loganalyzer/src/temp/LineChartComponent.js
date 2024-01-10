// LineChart.js
import React, { useRef, useEffect,useState } from 'react';
import Chart from 'chart.js/auto';

const LineChart = ({ logs }) => {
  const chartRef = useRef(null);
  const [hoveredLog, setHoveredLog] = useState(null);

  useEffect(() => {
    // Sort logs based on timestamp before rendering the chart
    const sortedLogs = logs.slice().sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

    if (chartRef.current && sortedLogs.length > 0) {
      const labels = sortedLogs.map(log => log.timestamp);
      const data = sortedLogs.map(log => {
        const logLevelToValue = {
          INFO: 1,
          DEBUG: 2,
          WARNING: 3,
          ERROR: 4,
        };
        return logLevelToValue[log.log_level] || 0;
      });

      const ctx = chartRef.current.getContext('2d');

      // Ensure that the chart instance is destroyed before creating a new one
      if (ctx.chart) {
        ctx.chart.destroy();
      }

      ctx.chart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [{
            label: 'Log Levels',
            data: data,
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1,
            fill: false,
          }],
        },
        options: {
          scales: {
            y: {
              ticks: {
                reverse: true,
                stepSize: 1,
                callback: value => {
                  const valueToLogLevel = {
                    1: 'INFO',
                    2: 'DEBUG',
                    3: 'WARN',
                    4: 'ERROR',
                  };
                  return valueToLogLevel[value] || '';
                },
              },
            },
          },
          plugins: {
            tooltip: {
              callbacks: {
                label: (context) => {
                  // Retrieve the corresponding log object for the hovered point
                  const index = context.dataIndex;
                  const hoveredLog = sortedLogs[index];
                  setHoveredLog(hoveredLog);
                  return `${hoveredLog.message}`;  // Return an empty string to prevent the default label
                },
              },
            },
          },
        
        },
        
      });
    }
  }, [logs]);

  return (
    <div>
      <h3>Line Chart</h3>
      <canvas ref={chartRef} width={800} height={400}></canvas>
    </div>
  );
};

export default LineChart;
