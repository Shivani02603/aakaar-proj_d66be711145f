.PHONY: install dev build test docker-up docker-down clean

install:
	# Install backend dependencies
	pip install -r backend/requirements.txt
	# Install frontend dependencies
	cd frontend && npm install

dev:
	# Start development environment
	./scripts/dev.sh

build:
	# Build frontend for production
	cd frontend && npm run build
	# Build Docker images
	docker-compose build

test:
	# Run backend tests
	pytest
	# Run frontend tests
	cd frontend && npm test

docker-up:
	# Start all services using Docker Compose
	docker-compose up -d

docker-down:
	# Stop all services
	docker-compose down

clean:
	# Remove Docker containers, images, and volumes
	docker-compose down --volumes --rmi all
	# Remove Python cache files
	find . -type d -name "__pycache__" -exec rm -r {} +
	# Remove node_modules
	rm -rf frontend/node_modules
	# Remove build artifacts
	rm -rf frontend/dist