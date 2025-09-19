# Makefile for FactForge model training pipeline

.PHONY: help data train evaluate clean all

# Default target
help:
	@echo "FactForge Model Training Pipeline"
	@echo "================================"
	@echo ""
	@echo "Available targets:"
	@echo "  data      - Prepare training data"
	@echo "  train     - Train the classifier model"
	@echo "  evaluate  - Evaluate the trained model"
	@echo "  clean     - Clean up generated files"
	@echo "  all       - Run complete pipeline (data + train + evaluate)"
	@echo "  help      - Show this help message"
	@echo ""
	@echo "Usage:"
	@echo "  make data      # Prepare training data"
	@echo "  make train     # Train model"
	@echo "  make evaluate  # Evaluate model"
	@echo "  make all       # Run complete pipeline"

# Data preparation
data:
	@echo "Preparing training data..."
	python data_prep.py
	@echo "Data preparation completed!"

# Model training
train:
	@echo "Training classifier model..."
	python train_classifier.py
	@echo "Model training completed!"

# Model evaluation
evaluate:
	@echo "Evaluating trained model..."
	python evaluate.py
	@echo "Model evaluation completed!"

# Clean up generated files
clean:
	@echo "Cleaning up generated files..."
	rm -rf data/
	rm -rf artifacts/
	rm -rf evaluation/
	rm -f *.log
	@echo "Cleanup completed!"

# Run complete pipeline
all: data train evaluate
	@echo "Complete pipeline finished!"

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "Dependencies installed!"

# Run tests
test:
	@echo "Running tests..."
	python -m pytest tests/ -v
	@echo "Tests completed!"

# Format code
format:
	@echo "Formatting code..."
	black *.py
	isort *.py
	@echo "Code formatted!"

# Lint code
lint:
	@echo "Linting code..."
	flake8 *.py
	mypy *.py
	@echo "Linting completed!"

# Check code quality
check: format lint test
	@echo "Code quality check completed!"

# Create virtual environment
venv:
	@echo "Creating virtual environment..."
	python -m venv venv
	@echo "Virtual environment created!"
	@echo "Activate with: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)"

# Setup development environment
setup: venv install
	@echo "Development environment setup completed!"
	@echo "Activate the virtual environment and run 'make data' to start"

# Show model info
info:
	@echo "Model Information"
	@echo "================="
	@echo "Data directory: data/"
	@echo "Artifacts directory: artifacts/"
	@echo "Evaluation directory: evaluation/"
	@echo ""
	@if [ -d "data" ]; then \
		echo "Data files:"; \
		ls -la data/; \
	fi
	@if [ -d "artifacts" ]; then \
		echo "Model artifacts:"; \
		ls -la artifacts/; \
	fi
	@if [ -d "evaluation" ]; then \
		echo "Evaluation results:"; \
		ls -la evaluation/; \
	fi

# Backup model artifacts
backup:
	@echo "Creating backup of model artifacts..."
	@if [ -d "artifacts" ]; then \
		tar -czf model_backup_$(shell date +%Y%m%d_%H%M%S).tar.gz artifacts/; \
		echo "Backup created: model_backup_$(shell date +%Y%m%d_%H%M%S).tar.gz"; \
	else \
		echo "No artifacts directory found to backup"; \
	fi

# Restore model artifacts
restore:
	@echo "Available backups:"
	@ls -la model_backup_*.tar.gz 2>/dev/null || echo "No backups found"
	@echo ""
	@echo "To restore a backup, run:"
	@echo "  tar -xzf model_backup_YYYYMMDD_HHMMSS.tar.gz"

# Show training progress
progress:
	@echo "Training Progress"
	@echo "================"
	@if [ -f "artifacts/training_log.txt" ]; then \
		echo "Latest training log:"; \
		tail -20 artifacts/training_log.txt; \
	else \
		echo "No training log found"; \
	fi

# Monitor system resources
monitor:
	@echo "System Resources"
	@echo "================"
	@echo "CPU Usage:"
	@top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1
	@echo "Memory Usage:"
	@free -h | grep "Mem:"
	@echo "Disk Usage:"
	@df -h . | tail -1

# Generate model report
report:
	@echo "Generating model report..."
	@if [ -f "evaluation/evaluation_report.md" ]; then \
		echo "Evaluation report available at: evaluation/evaluation_report.md"; \
		head -20 evaluation/evaluation_report.md; \
	else \
		echo "No evaluation report found. Run 'make evaluate' first."; \
	fi

# Deploy model
deploy:
	@echo "Deploying model..."
	@if [ -d "artifacts" ]; then \
		echo "Model artifacts found. Copying to production..."; \
		cp -r artifacts/ ../api/models/; \
		echo "Model deployed to API directory"; \
	else \
		echo "No model artifacts found. Run 'make train' first."; \
	fi

# Validate model
validate:
	@echo "Validating model..."
	@if [ -f "artifacts/model.pkl" ]; then \
		echo "Model file exists"; \
		python -c "import pickle; model = pickle.load(open('artifacts/model.pkl', 'rb')); print('Model loaded successfully')"; \
	else \
		echo "Model file not found. Run 'make train' first."; \
	fi

# Show help for specific target
%:
	@echo "Help for target: $@"
	@echo "=================="
	@echo "This target is not documented. Run 'make help' for available targets."
