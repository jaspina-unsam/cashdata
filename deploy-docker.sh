#!/bin/bash

echo "🔨 Building and deploying with Docker..."

# Stop any running containers
echo "📦 Stopping existing containers..."
docker-compose down

# Build frontend for production
echo "🎨 Building frontend..."
cd frontend
npm run build
cd ..

# Build and start Docker containers
echo "🐳 Building Docker images..."
docker-compose build

echo "🚀 Starting containers..."
docker-compose up -d

# Wait a bit for services to start
sleep 5

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📱 Frontend: http://localhost"
echo "🔌 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
