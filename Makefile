.PHONY: lint, typecheck, test, ci, load_test_req, load_test, bento_test \
		up_cpu_recognition down_cpu_recognition up_gpu_recognition down_gpu_recognition \
		up_storage down_storage up_identity down_identity up_glitchtip down_glitchtip \
		up_cpu_system_minimal down_cpu_system_minimal up_cpu_system down_cpu_system \
		up_gpu_system_minimal down_gpu_system_minimal up_gpu_system down_gpu_system \
		up_cpu_system_nano down_cpu_system_nano up_gpu_system_nano down_gpu_system_nano

ENV_FILE ?= .env-dev
STORAGE_PATH ?= ./storage
IDENTITY_PATH ?= ./identity
GLITCHTIP_PATH ?= ./glitchtip

load_test_req:
	pip install -r ./inference/tests/locustfiles/requirements.txt

load_test: load_test_req
	locust

bento_test:
	cd inference && \
	pip install -r requirements_test.txt && \
	pytest --verbosity=1 -s

lint:
	flake8 .

typecheck:
	mypy .

test:
	pytest inference/tests queue_handler/tests

ci: lint typecheck test

up_cpu_recognition:
	docker compose --env-file="${ENV_FILE}" up -d
down_cpu_recognition:
	docker compose --env-file="${ENV_FILE}" down

up_gpu_recognition:
	docker compose --env-file="${ENV_FILE}" -f "./docker-compose-gpu.yaml" up -d
down_gpu_recognition:
	docker compose --env-file="${ENV_FILE}" -f "./docker-compose-gpu.yaml" down

up_storage:
	docker compose -f "${STORAGE_PATH}/docker-compose.yaml" --env-file="${STORAGE_PATH}/${ENV_FILE}" up -d
down_storage:
	docker compose -f "${STORAGE_PATH}/docker-compose.yaml" --env-file="${STORAGE_PATH}/${ENV_FILE}" down

up_identity:
	docker compose -f "${IDENTITY_PATH}/docker-compose.yaml" --env-file="${IDENTITY_PATH}/${ENV_FILE}" up -d
down_identity:
	docker compose -f "${IDENTITY_PATH}/docker-compose.yaml" --env-file="${IDENTITY_PATH}/${ENV_FILE}" down

up_glitchtip:
	docker compose -f "${GLITCHTIP_PATH}/docker-compose.yaml" up -d
down_glitchtip:
	docker compose -f "${GLITCHTIP_PATH}/docker-compose.yaml" down

up_cpu_system_nano: up_identity up_cpu_recognition
down_cpu_system_nano: down_identity down_cpu_recognition

up_cpu_system_minimal: up_identity up_cpu_recognition up_storage
down_cpu_system_minimal: down_identity down_cpu_recognition down_storage

up_cpu_system: up_identity up_cpu_recognition up_storage up_glitchtip
down_cpu_system: down_identity down_cpu_recognition down_storage down_glitchtip

up_gpu_system_nano: up_identity up_gpu_recognition
down_gpu_system_nano: down_identity down_gpu_recognition

up_gpu_system_minimal: up_identity up_gpu_recognition up_storage
down_gpu_system_minimal: down_identity down_gpu_recognition down_storage

up_gpu_system: up_identity up_gpu_recognition up_storage  up_glitchtip
down_gpu_system: down_identity down_gpu_recognition down_storage  down_glitchtip