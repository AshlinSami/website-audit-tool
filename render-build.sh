#!/bin/bash
set -e

echo "📦 Installing Python dependencies..."
cd web-app
pip install -r requirements.txt

echo "🌐 Installing Chrome and dependencies..."
apt-get update
apt-get install -y wget gnupg ca-certificates
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
apt-get update
apt-get install -y google-chrome-stable

# Install chromium as fallback
apt-get install -y chromium chromium-driver || true

echo "✅ Build complete!"
