.PHONY: clean build dependency

clean:
	rm -rf build/
	rm *.spec

build:
	pyinstaller clipanda.py --onefile
	make clean

dependency:
	python3 -m pip install pyinstaller requests