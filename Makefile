PYTHON=python3
SRC=init.py
OUT=dist
EXE=$(OUT)/DrLogger.exe
TEST_DIR=test

.PHONY: all prep build run run-exec test clean

all: build run-exec

prep: requirements.txt
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

build: prep $(EXE)
	$(PYTHON) -m PyInstaller --onefile --noconsole --name DrLogger --add-data "resources;resources" $(SRC)

run: prep
	$(PYTHON) $(SRC)

run-exec: build $(EXE)
	$(EXE)

test: prep
	$(PYTHON) -m unittest discover $(TEST_DIR)

clean:
	del /Q /S $(OUT)