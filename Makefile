.PHONY: build dependency 

dependency:
	python3 -m pip install pyinstaller requests

install:
	cp ./clipanda.py ~/.local/bin/clipanda
	chmod u+x ~/.local/bin/clipanda
