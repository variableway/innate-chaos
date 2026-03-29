.PHONY: help setup start stop restart logs clean backend frontend test

help: ## Show this help message
	@echo "HyperTrace - Trading Signal Dashboard"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Initial setup - create env files and build
	@./scripts/setup.sh

start: ## Start all services
	@docker-compose up -d
	@echo "✅ Services started"
	@echo "📊 Dashboard: http://localhost:3000"
	@echo "📚 API Docs:   http://localhost:8000/docs"

stop: ## Stop all services
	@docker-compose down
	@echo "🛑 Services stopped"

restart: ## Restart all services
	@docker-compose restart
	@echo "🔄 Services restarted"

logs: ## View logs from all services
	@docker-compose logs -f

logs-backend: ## View backend logs only
	@docker-compose logs -f backend

logs-frontend: ## View frontend logs only
	@docker-compose logs -f frontend

clean: ## Stop and remove all containers and volumes
	@docker-compose down -v
	@docker system prune -f
	@echo "🧹 Cleanup complete"

backend-shell: ## Open a shell in the backend container
	@docker-compose exec backend bash

frontend-shell: ## Open a shell in the frontend container
	@docker-compose exec frontend sh

db-shell: ## Open PostgreSQL shell
	@docker-compose exec db psql -U hypertrace -d hypertrace

test-backend: ## Run backend tests
	@cd backend && python -m pytest

format-backend: ## Format backend code
	@cd backend && black . && isort .

lint-backend: ## Lint backend code
	@cd backend && flake8 . && pylint app

build: ## Build all Docker images
	@docker-compose build

pull: ## Pull latest images
	@docker-compose pull
