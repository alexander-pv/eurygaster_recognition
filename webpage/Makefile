.PHONY: clean install uninstall

clean:
	python setup.py clean --all
	rm -rf build eurygaster_webpage.egg-info

install: clean
	pip install .
	make clean

uninstall:
	pip uninstall -y eurygaster_webpage
