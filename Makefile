PYTHON := python3
VENV := .venv
SRC := src
DIST := dist
APP_NAME := DrLogger
REQS := requirements.txt

.PHONY: all clean run run-exec

all: build

$(VENV) $(VENV)/Scripts/python $(VENV)/Scripts/activate:
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

$(DIST)/$(APP_NAME).exe: $(VENV)/Scripts/python $(APP_NAME).spec
	@echo "Building executable..."
	@PYTHONPATH=src $(VENV)/Scripts/python -m PyInstaller $(APP_NAME).spec

run: $(VENV)/Scripts/python
	@echo "Run Executable..."
	@PYTHONPATH=src $(VENV)/Scripts/python $(SRC)/init.py

run-exec: $(VENV)/Scripts/activate $(DIST)/$(APP_NAME).exe
	@. $(VENV)/Scripts/activate && ./$(DIST)/$(APP_NAME).exe

clean:
	rm -rf build dist $(VENV)
