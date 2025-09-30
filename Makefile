PYTHON := python3
VENV := .venv
SRC_DIR := src
DIST_DIR := dist
TEST_DIR := $(SRC_DIR)/test
APP_NAME := DrLogger
REQS := requirements.txt

SPEC_FILE := $(APP_NAME).spec

OUT_EXEC := $(DIST_DIR)/$(APP_NAME).exe

.PHONY: all build run-test clean

all: run-test build

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

$(OUT_EXEC): $(VENV) $(SPEC_FILE) $(SRC_DIR)
	@echo "Building executable..."
	@PYTHONPATH=$(SRC_DIR) $(VENV)/Scripts/python -m PyInstaller $(SPEC_FILE)

build: $(OUT_EXEC)

run-test: $(VENV) $(SRC_DIR)
	@echo "Run Tests..."
	@PYTHONPATH=$(SRC_DIR) $(VENV)/Scripts/python -m unittest discover -s $(TEST_DIR)

clean:
	rm -rf build dist $(VENV)
