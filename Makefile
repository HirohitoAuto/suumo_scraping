build:
	docker build -t suumo_scraping .

run:
	docker run -it --rm \
		-v ./scraping/:/app/scraping \
		suumo_scraping bash
