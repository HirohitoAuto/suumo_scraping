build_scraping:
	docker build -t suumo_scraping -f Dockerfile.scraping . --no-cache

run_scraping:
	docker run -it \
		-v ./scraping/:/usr/scraping \
		suumo_scraping bash

build_streamlit:
	docker build -t suumo_streamlit -f Dockerlsfile.streamlit . --no-cache

run_streamlit:
	docker run -it \
		-p 8501:8501 \
		-v ./streamlit/:/usr/streamlit \
		-v ./scraping/data/:/usr/streamlit/data \
		suumo_streamlit bash