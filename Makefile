build:
	docker build -t suumo_scraping .

run:
	docker run -it --rm \
		-v ./scraping/:/app/scraping \
		suumo_scraping bash

dry-run:
	docker run -it --rm \
		-v ./scraping/:/app/scraping \
		suumo_scraping uv run python -m scraping fukuoka_convinient --dry-run

test-run:
	docker run -it --rm \
		-v ./scraping/:/app/scraping \
		suumo_scraping uv run python -m scraping fukuoka_convinient --test-run
