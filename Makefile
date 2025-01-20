up:
			docker compose up -d

down:
			docker compose down

build:
			docker build -t kafka-job .
.PHONY: up down build
