.PHONY: clean build

clean:
	rm -rf build/
	rm *.spec

build:
	pyinstaller clipanda.py --onefile
	make clean
