.PHONY: clean build dependency buildwin

clean:
	rm -rf build/
	rm *.spec

buildwin:
	pyinstaller clipanda.py --windowed --onefile
	make clean

build:
	pyinstaller clipanda.py --onefile
	make clean

dependency:
	python3 -m pip install pyinstaller requests