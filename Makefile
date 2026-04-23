IMAGE_NAME=projetalgorithmique2groupe7
IMAGE_TAG=latest
REGISTRY=<adresse-registry-polytech>

.PHONY: build push run logs stop

build:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

push:
	docker tag $(IMAGE_NAME):$(IMAGE_TAG) $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)
	docker push $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)

run:
	docker compose -f deploy/docker-compose.yaml up -d

logs:
	docker compose -f deploy/docker-compose.yaml logs -f

stop:
	docker compose -f deploy/docker-compose.yaml down