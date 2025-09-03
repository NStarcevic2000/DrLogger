PYTHON=python3
SRC=init.py
EXE=dist/DrLog.exe
TEST_DIR=test

.PHONY: all build test clean

all: build

build:
	$(PYTHON) -m pip install --upgrade pip pyinstaller
	$(PYTHON) -m PyInstaller --onefile $(SRC) --distpath dist

run:
	$(PYTHON) $(SRC)

run-exec:
	$(EXE)

test:
	$(PYTHON) -m unittest discover $(TEST_DIR)

clean:
	rm -rf build dist __pycache__ *.spec