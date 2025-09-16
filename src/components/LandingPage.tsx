import React, { useState, useEffect } from 'react';
import PerformanceChart from './PerformanceChart';
import RevenueTracker from './RevenueTracker';
import AgentControls from './AgentControls';
import './LandingPage.css';

interface CallStats {
  success: number;
  rejected: number;
  voicemail: number;
  forwarded: number;
}

interface RevenueData {
  dailyRevenue: number;
  successRate: number;
  totalCalls: number;
}

const LandingPage: React.FC = () => {
  const [callStats, setCallStats] = useState<CallStats>({
    success: 0,
    rejected: 0,
    voicemail: 0,
    forwarded: 0
  });

  const [revenueData, setRevenueData] = useState<RevenueData>({
    dailyRevenue: 0,
    successRate: 0,
    totalCalls: 0
  });

  const [isAgentRunning, setIsAgentRunning] = useState(false);

  // Simulate real-time data updates
  useEffect(() => {
    const interval = setInterval(() => {
      if (isAgentRunning) {
        // Simulate random data updates
        setCallStats(prev => ({
          success: prev.success + Math.floor(Math.random() * 3),
          rejected: prev.rejected + Math.floor(Math.random() * 2),
          voicemail: prev.voicemail + Math.floor(Math.random() * 2),
          forwarded: prev.forwarded + Math.floor(Math.random() * 1)
        }));

        setRevenueData(prev => {
          const newSuccess = Math.floor(Math.random() * 3);
          const revenuePerSuccess = 25; // $25 per successful sale
          return {
            dailyRevenue: prev.dailyRevenue + (newSuccess * revenuePerSuccess),
            successRate: prev.totalCalls > 0 ? (prev.successRate * prev.totalCalls + newSuccess) / (prev.totalCalls + 1) : 0,
            totalCalls: prev.totalCalls + 1
          };
        });
      }
    }, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, [isAgentRunning]);

  const handleAgentToggle = (running: boolean) => {
    setIsAgentRunning(running);
  };

  return (
    <div className="landing-page">
      <header className="header">
        <h1>AI Agent Dashboard</h1>
        <p>Sports Ticket Sales Performance Monitor</p>
      </header>

      <div className="dashboard-grid">
        <div className="chart-section">
          <PerformanceChart data={callStats} />
        </div>
        
        <div className="revenue-section">
          <RevenueTracker data={revenueData} />
        </div>
        
        <div className="agent-section">
          <AgentControls 
            isRunning={isAgentRunning}
            onToggle={handleAgentToggle}
          />
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
