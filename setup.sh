#!/bin/bash

echo "🚀 Setting up AI Agent Dashboard Frontend..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 16 ]; then
    echo "❌ Node.js version 16+ is required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js version: $(node -v)"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
    echo ""
    echo "🎉 Setup complete! You can now run:"
    echo "   npm start    - Start development server"
    echo "   npm build    - Build for production"
    echo ""
    echo "📝 Don't forget to:"
    echo "   1. Create a .env file with your API URL"
    echo "   2. Update the API endpoints in src/services/api.ts"
    echo "   3. Start your backend server"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi
