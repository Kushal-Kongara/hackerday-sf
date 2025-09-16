import React, { useEffect, useRef } from 'react';

interface VapiWidgetProps {
  isVisible: boolean;
  onClose: () => void;
}

declare global {
  interface Window {
    VapiWidget: any;
  }
}

const VapiWidget: React.FC<VapiWidgetProps> = ({ isVisible, onClose }) => {
  const widgetRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isVisible && window.VapiWidget) {
      // Create the Vapi widget element
      const widgetElement = document.createElement('vapi-widget');
      widgetElement.setAttribute('assistant-id', 'aa926c06-a58c-4024-a48a-d4bea581c23a');
      widgetElement.setAttribute('public-key', '635b3410-98b0-4cb4-b5f5-09d00df6aec8');
      
      if (widgetRef.current) {
        widgetRef.current.appendChild(widgetElement);
      }
    }
  }, [isVisible]);

  if (!isVisible) return null;

  return (
    <div className="vapi-widget-overlay">
      <div className="vapi-widget-container">
        <div className="vapi-widget-header">
          <h3>AI Agent Conversation</h3>
          <button className="close-widget" onClick={onClose}>
            ×
          </button>
        </div>
        <div className="vapi-widget-content" ref={widgetRef}>
          {/* Vapi widget will be inserted here */}
        </div>
      </div>
    </div>
  );
};

export default VapiWidget;
