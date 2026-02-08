.PHONY: help build up down restart logs clean test dev prod

# Default target
help:
	@echo "MOSAIC - Multimodal Video Analysis Platform"
	@echo ""
	@echo "Available commands:"
	@echo "  make build         - Build all Docker images"
	@echo "  make up            - Start all services (production mode)"
	@echo "  make dev           - Start all services (development mode with hot reload)"
	@echo "  make down          - Stop all services"
	@echo "  make restart       - Restart all services"
	@echo "  make logs          - View logs from all services"
	@echo "  make logs-api      - View API server logs"
	@echo "  make logs-mcp      - View MCP server logs"
	@echo "  make logs-ui       - View frontend logs"
	@echo "  make clean         - Remove all containers, volumes, and images"
	@echo "  make test          - Run all tests"
	@echo "  make test-api      - Run API tests"
	@echo "  make test-mcp      - Run MCP tests"
	@echo "  make setup         - Initial setup (copy .env.example to .env)"
	@echo "  make shell-api     - Open shell in API container"
	@echo "  make shell-mcp     - Open shell in MCP container"
	@echo "  make shell-ui      - Open shell in UI container"
	@echo "  make ps            - Show running containers"
	@echo "  make prune         - Clean up Docker system"

# Initial setup
setup:
	@echo "Setting up MOSAIC..."
	@if not exist .env copy .env.example .env
	@echo "Created .env file from .env.example"
	@echo "Please edit .env and add your API keys before running 'make up'"

# Build Docker images
build:
	@echo "Building Docker images..."
	docker-compose build

# Start services in production mode
up:
	@echo "Starting MOSAIC services (production)..."
	docker-compose up -d
	@echo "Services started!"
	@echo "Frontend: http://localhost:3000"
	@echo "API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

# Start services in production mode with logs
up-logs:
	@echo "Starting MOSAIC services (production) with logs..."
	docker-compose up

# Start services in development mode
dev:
	@echo "Starting MOSAIC services (development mode)..."
	docker-compose -f docker-compose.dev.yml up
	@echo "Development mode enabled with hot reload"

# Start services in development mode (detached)
dev-d:
	@echo "Starting MOSAIC services (development mode, detached)..."
	docker-compose -f docker-compose.dev.yml up -d
	@echo "Services started in background!"

# Stop services
down:
	@echo "Stopping MOSAIC services..."
	docker-compose down
	docker-compose -f docker-compose.dev.yml down

# Restart services
restart: down up

# View logs
logs:
	docker-compose logs -f

logs-api:
	docker-compose logs -f api-server

logs-mcp:
	docker-compose logs -f mcp-server

logs-ui:
	docker-compose logs -f frontend

# Show running containers
ps:
	docker-compose ps

# Clean up everything
clean:
	@echo "Cleaning up Docker resources..."
	docker-compose down -v --rmi all --remove-orphans
	docker-compose -f docker-compose.dev.yml down -v --rmi all --remove-orphans
	@echo "Cleaned up!"

# Deep clean including storage
clean-all: clean
	@echo "WARNING: This will delete all stored data!"
	@echo "Press Ctrl+C to cancel or wait 5 seconds..."
	@timeout /t 5
	@if exist storage rmdir /s /q storage
	@echo "All data cleaned!"

# Prune Docker system
prune:
	@echo "Pruning Docker system..."
	docker system prune -af --volumes
	@echo "Docker system pruned!"

# Run all tests
test:
	@echo "Running all tests..."
	docker-compose run --rm api-server pytest tests/ -v
	docker-compose run --rm mcp-server pytest tests/ -v

# Run API tests
test-api:
	@echo "Running API tests..."
	docker-compose run --rm api-server pytest tests/ -v

# Run MCP tests
test-mcp:
	@echo "Running MCP tests..."
	docker-compose run --rm mcp-server pytest tests/ -v

# Open shell in containers
shell-api:
	docker-compose exec api-server /bin/bash

shell-mcp:
	docker-compose exec mcp-server /bin/bash

shell-ui:
	docker-compose exec frontend /bin/sh

# Install dependencies locally (for development without Docker)
install-api:
	cd mosaic-api && pip install -r requirements.txt

install-mcp:
	cd mosaic-mcp && pip install -r requirements.txt

install-ui:
	cd mosaic-ui && npm install

install: install-api install-mcp install-ui
	@echo "All dependencies installed!"

# Format code
format:
	@echo "Formatting Python code..."
	cd mosaic-api && black app/ tests/
	cd mosaic-mcp && black src/ tests/
	@echo "Code formatted!"

# Lint code
lint:
	@echo "Linting Python code..."
	cd mosaic-api && ruff check app/ tests/
	cd mosaic-mcp && ruff check src/ tests/
	@echo "Linting complete!"

# Check code quality
quality: format lint
	@echo "Code quality check complete!"

# Rebuild specific service
rebuild-api:
	docker-compose build --no-cache api-server

rebuild-mcp:
	docker-compose build --no-cache mcp-server

rebuild-ui:
	docker-compose build --no-cache frontend

# Health check
health:
	@echo "Checking service health..."
	@curl -s http://localhost:8000/health || echo "API server not responding"
	@curl -s http://localhost:9090/health || echo "MCP server not responding"
	@curl -s http://localhost:3000/ > nul || echo "Frontend not responding"

# Database operations
db-reset:
	@echo "Resetting database..."
	@if exist storage\mosaic.db del storage\mosaic.db
	@echo "Database reset!"

# Backup storage
backup:
	@echo "Creating backup..."
	@if not exist backups mkdir backups
	@echo "Backing up storage..."
	@xcopy /E /I /Y storage backups\storage_%date:~-4,4%%date:~-10,2%%date:~-7,2%
	@echo "Backup created!"

# Show help
info:
	@echo "MOSAIC Project Information"
	@echo "=========================="
	@echo "Services:"
	@echo "  - Frontend (Next.js):  http://localhost:3000"
	@echo "  - API (FastAPI):       http://localhost:8000"
	@echo "  - API Docs (Swagger):  http://localhost:8000/docs"
	@echo "  - MCP Server:          http://localhost:9090"
	@echo ""
	@echo "Volumes:"
	@docker volume ls | findstr mosaic || echo "No volumes found"
	@echo ""
	@echo "Images:"
	@docker images | findstr mosaic || echo "No images found"
