.PHONY: install build dev preview clean docker-build docker-run

install:
	npm install

build:
	npm run build

dev:
	npm run dev

preview:
	npm run preview

clean:
	rm -rf dist node_modules

docker-build:
	docker build -t eurygaster-webpage-v2:latest .

docker-run:
	docker run -d \
		--name eurygaster-webpage-v2 \
		-p 4452:4452 \
		eurygaster-webpage-v2:latest

