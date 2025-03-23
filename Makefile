build:
	docker build -t suumo_streamlit -f Dockerfile.streamlit . --no-cache

run:
	docker run -it \
		-p 8501:8501 \
		-v ./streamlit/:/usr/streamlit \
		-v ./data/:/usr/streamlit/data \
		suumo_streamlit bash