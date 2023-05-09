.PHONY: install uninstall clean

clean:
	python setup.py clean --all
	rm -rf ./build ./dist ./queue_handler.egg-info

install:
	pip install .
	make clean

uninstall:
	pip uninstall -y queue_handler
