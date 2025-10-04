.PHONY: install uninstall build clean publish test help

help:
	@echo "QVenv Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  make install    - Install qvenv globally (runs install.sh)"
	@echo "  make uninstall  - Uninstall qvenv"
	@echo "  make build      - Build distribution packages"
	@echo "  make publish    - Build and publish to PyPI"
	@echo "  make clean      - Remove build artifacts"
	@echo "  make test       - Run tests"
	@echo "  make help       - Show this help message"

install:
	@echo "Installing qvenv..."
	@bash install.sh

uninstall:
	@echo "Uninstalling qvenv..."
	@rm -f /usr/local/bin/qvenv ~/.local/bin/qvenv
	@# Remove from shell configs
	@if [ -f "$$HOME/.zshrc" ]; then \
		sed -i.bak '/# QVenv auto-activation/d' "$$HOME/.zshrc" 2>/dev/null || true; \
		sed -i.bak '/source.*qvenv\.sh/d' "$$HOME/.zshrc" 2>/dev/null || true; \
		rm -f "$$HOME/.zshrc.bak"; \
	fi
	@if [ -f "$$HOME/.bashrc" ]; then \
		sed -i.bak '/# QVenv auto-activation/d' "$$HOME/.bashrc" 2>/dev/null || true; \
		sed -i.bak '/source.*qvenv\.sh/d' "$$HOME/.bashrc" 2>/dev/null || true; \
		rm -f "$$HOME/.bashrc.bak"; \
	fi
	@echo "Uninstalled successfully!"

clean:
	@echo "Cleaning build artifacts..."
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info
	@rm -rf __pycache__
	@find . -type f -name '*.pyc' -delete
	@find . -type d -name '__pycache__' -delete
	@echo "Clean complete!"

build: clean
	@echo "Building distribution packages..."
	@python3 -m pip install --upgrade build twine
	@python3 -m build
	@echo "Build complete! Packages in dist/"

publish: build
	@echo "Publishing to PyPI..."
	@python3 -m twine upload dist/*
	@echo "Published successfully!"

test:
	@echo "Running tests..."
	@python3 qvenv.py --help
	@echo "Basic test passed!"

