import React, { useState } from 'react';
import { 
  Play, 
  Pause, 
  Square, 
  Settings, 
  Activity, 
  Users, 
  Clock,
  Target,
  Zap,
  Brain
} from 'lucide-react';
import './AgentControls.css';

interface AgentControlsProps {
  isRunning: boolean;
  onToggle: (running: boolean) => void;
}

const AgentControls: React.FC<AgentControlsProps> = ({ isRunning, onToggle }) => {
  const [showSettings, setShowSettings] = useState(false);
  const [agentConfig, setAgentConfig] = useState({
    maxCallsPerHour: 20,
    callDuration: 300, // 5 minutes in seconds
    retryAttempts: 2,
    voiceModel: 'premium',
    targetAudience: 'sports-fans'
  });

  const handleStart = () => {
    onToggle(true);
  };

  const handleStop = () => {
    onToggle(false);
  };

  const handlePause = () => {
    onToggle(false);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const agentStats = {
    activeAgents: isRunning ? 1 : 0,
    totalAgents: 1,
    avgCallDuration: '4:32',
    callsInQueue: isRunning ? 15 : 0,
    nextCallIn: isRunning ? '00:45' : '--:--'
  };

  return (
    <div className="agent-controls">
      <div className="controls-header">
        <div className="header-left">
          <h2>AI Agent Control Center</h2>
          <div className="agent-status">
            <div className={`status-indicator ${isRunning ? 'running' : 'stopped'}`}>
              <Activity size={16} />
              <span>{isRunning ? 'Active' : 'Stopped'}</span>
            </div>
          </div>
        </div>
        <button 
          className="settings-btn"
          onClick={() => setShowSettings(!showSettings)}
        >
          <Settings size={20} />
        </button>
      </div>

      <div className="controls-main">
        <div className="control-buttons">
          <button 
            className={`control-btn start-btn ${isRunning ? 'disabled' : ''}`}
            onClick={handleStart}
            disabled={isRunning}
          >
            <Play size={20} />
            <span>Start Agent</span>
          </button>
          
          <button 
            className={`control-btn pause-btn ${!isRunning ? 'disabled' : ''}`}
            onClick={handlePause}
            disabled={!isRunning}
          >
            <Pause size={20} />
            <span>Pause</span>
          </button>
          
          <button 
            className={`control-btn stop-btn ${!isRunning ? 'disabled' : ''}`}
            onClick={handleStop}
            disabled={!isRunning}
          >
            <Square size={20} />
            <span>Stop</span>
          </button>
        </div>

        <div className="agent-stats">
          <div className="stat-grid">
            <div className="stat-item">
              <div className="stat-icon">
                <Users size={18} />
              </div>
              <div className="stat-content">
                <div className="stat-label">Active Agents</div>
                <div className="stat-value">
                  {agentStats.activeAgents}/{agentStats.totalAgents}
                </div>
              </div>
            </div>

            <div className="stat-item">
              <div className="stat-icon">
                <Clock size={18} />
              </div>
              <div className="stat-content">
                <div className="stat-label">Avg. Call Duration</div>
                <div className="stat-value">{agentStats.avgCallDuration}</div>
              </div>
            </div>

            <div className="stat-item">
              <div className="stat-icon">
                <Target size={18} />
              </div>
              <div className="stat-content">
                <div className="stat-label">Calls in Queue</div>
                <div className="stat-value">{agentStats.callsInQueue}</div>
              </div>
            </div>

            <div className="stat-item">
              <div className="stat-icon">
                <Zap size={18} />
              </div>
              <div className="stat-content">
                <div className="stat-label">Next Call In</div>
                <div className="stat-value">{agentStats.nextCallIn}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {showSettings && (
        <div className="settings-panel">
          <div className="settings-header">
            <h3>Agent Configuration</h3>
            <button 
              className="close-settings"
              onClick={() => setShowSettings(false)}
            >
              ×
            </button>
          </div>
          
          <div className="settings-content">
            <div className="setting-group">
              <label>Max Calls Per Hour</label>
              <input 
                type="number" 
                value={agentConfig.maxCallsPerHour}
                onChange={(e) => setAgentConfig({
                  ...agentConfig,
                  maxCallsPerHour: parseInt(e.target.value)
                })}
                min="1"
                max="100"
              />
            </div>

            <div className="setting-group">
              <label>Call Duration (seconds)</label>
              <input 
                type="number" 
                value={agentConfig.callDuration}
                onChange={(e) => setAgentConfig({
                  ...agentConfig,
                  callDuration: parseInt(e.target.value)
                })}
                min="60"
                max="1800"
              />
            </div>

            <div className="setting-group">
              <label>Retry Attempts</label>
              <input 
                type="number" 
                value={agentConfig.retryAttempts}
                onChange={(e) => setAgentConfig({
                  ...agentConfig,
                  retryAttempts: parseInt(e.target.value)
                })}
                min="0"
                max="5"
              />
            </div>

            <div className="setting-group">
              <label>Voice Model</label>
              <select 
                value={agentConfig.voiceModel}
                onChange={(e) => setAgentConfig({
                  ...agentConfig,
                  voiceModel: e.target.value
                })}
              >
                <option value="premium">Premium</option>
                <option value="standard">Standard</option>
                <option value="basic">Basic</option>
              </select>
            </div>

            <div className="setting-group">
              <label>Target Audience</label>
              <select 
                value={agentConfig.targetAudience}
                onChange={(e) => setAgentConfig({
                  ...agentConfig,
                  targetAudience: e.target.value
                })}
              >
                <option value="sports-fans">Sports Fans</option>
                <option value="general">General</option>
                <option value="premium">Premium Customers</option>
              </select>
            </div>
          </div>

          <div className="settings-actions">
            <button className="save-btn">Save Configuration</button>
            <button className="reset-btn">Reset to Default</button>
          </div>
        </div>
      )}

      <div className="agent-info">
        <div className="info-item">
          <Brain size={16} />
          <span>AI-Powered Voice Agent</span>
        </div>
        <div className="info-item">
          <Target size={16} />
          <span>Sports Ticket Sales Focus</span>
        </div>
        <div className="info-item">
          <Zap size={16} />
          <span>Real-time Performance Tracking</span>
        </div>
      </div>
    </div>
  );
};

export default AgentControls;
