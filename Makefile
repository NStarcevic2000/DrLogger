PYTHON := python3
VENV := .venv
SRC_DIR := src
DIST_DIR := dist
TEST_DIR := $(SRC_DIR)/test
APP_NAME := DrLogger
REQS := requirements.txt

SPEC_FILE := $(APP_NAME).spec

OUT_EXEC := $(DIST_DIR)/$(APP_NAME).exe

.PHONY: all build test clean run run-exec

all: $(OUT_EXEC)

$(VENV):
	@if ! command -v $(PYTHON) >/dev/null 2>&1; then \
		echo "$(PYTHON) not found. Please install Python 3.6+"; \
		exit 1; \
	fi
	@if [ ! -d "$(VENV)" ]; then \
		echo "Creating virtual environment..."; \
		$(PYTHON) -m venv $(VENV); \
	fi
	@. $(VENV)/Scripts/activate && python -m pip install --upgrade pip
	@. $(VENV)/Scripts/activate && pip install -r $(REQS)
	@. $(VENV)/Scripts/activate && pip install --upgrade pyinstaller

$(OUT_EXEC): $(VENV) $(SPEC_FILE)
	@echo "Building executable..."
	@PYTHONPATH=src $(VENV)/Scripts/python -m PyInstaller --clean --noconfirm $(SPEC_FILE)

run-test: $(VENV)
	@echo "Run Tests..."
	@PYTHONPATH=src $(VENV)/Scripts/python -m unittest discover -s $(TEST_DIR)

clean:
	rm -rf build dist $(VENV)
