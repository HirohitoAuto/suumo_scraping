build_scraping:
	docker build -t suumo_scraping -f Dockerfile.scraping . --no-cache

run_scraping:
	docker run -it \
		-v ./scraping/:/usr/scraping \
		suumo_scraping bash
