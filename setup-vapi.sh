#!/bin/bash

echo "🚀 Setting up Vapi integration..."

# Create .env file with Vapi API key
cat > .env << EOF
# Vapi Configuration
REACT_APP_VAPI_API_KEY=654fde54-9261-4710-877b-a6bd6ff9a840

# Backend API Configuration
REACT_APP_API_URL=http://localhost:8000

# Optional: WebSocket URL for real-time updates
REACT_APP_WS_URL=ws://localhost:8000/ws
EOF

echo "✅ Environment file created with your Vapi API key"
echo ""
echo "📝 Next steps:"
echo "1. Get your Vapi Assistant ID from https://dashboard.vapi.ai"
echo "2. Open the dashboard and click the settings button"
echo "3. Enter your Assistant ID in the configuration panel"
echo "4. Enter the target phone number"
echo "5. Click 'Start Agent' to make your first call!"
echo ""
echo "🎉 Vapi integration is ready!"
