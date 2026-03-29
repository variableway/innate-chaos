#!/bin/bash

# HyperTrace Setup Script

set -e

echo "🚀 HyperTrace Setup"
echo "===================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose found"

# Create environment files if they don't exist
if [ ! -f "backend/.env" ]; then
    echo "📝 Creating backend/.env..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please edit backend/.env with your configuration"
fi

if [ ! -f "frontend/.env.local" ]; then
    echo "📝 Creating frontend/.env.local..."
    cp frontend/.env.local.example frontend/.env.local
    echo "⚠️  Please edit frontend/.env.local with your configuration"
fi

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "✅ HyperTrace is starting up!"
echo ""
echo "📊 Dashboard: http://localhost:3000"
echo "📚 API Docs:   http://localhost:8000/docs"
echo "🔍 Health:     http://localhost:8000/health"
echo ""
echo "📋 Useful commands:"
echo "  View logs:        docker-compose logs -f"
echo "  Stop services:    docker-compose down"
echo "  Restart:          docker-compose restart"
echo ""
echo "⚠️  Note: It may take a few moments for all services to be ready."
