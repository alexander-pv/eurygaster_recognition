.PHONY: bento_test \
		up_cpu_recognition down_cpu_recognition \
		up_storage down_storage up_identity down_identity \
		up_cpu_system_minimal down_cpu_system_minimal up_cpu_system down_cpu_system \
		up_cpu_system_nano down_cpu_system_nano

ENV_FILE ?= .env-dev
STORAGE_PATH ?= ./src/storage
IDENTITY_PATH ?= ./src/identity

bento_test:
	cd src/inference && \
	pip install -r requirements_test.txt && \
	pytest --verbosity=1 -s

up_cpu_recognition:
	docker compose --env-file="${ENV_FILE}" up -d
down_cpu_recognition:
	docker compose --env-file="${ENV_FILE}" down

up_storage:
	docker compose -f "${STORAGE_PATH}/docker-compose.yaml" --env-file="${STORAGE_PATH}/${ENV_FILE}" up -d
down_storage:
	docker compose -f "${STORAGE_PATH}/docker-compose.yaml" --env-file="${STORAGE_PATH}/${ENV_FILE}" down

up_identity:
	docker compose -f "${IDENTITY_PATH}/docker-compose.yaml" --env-file="${IDENTITY_PATH}/${ENV_FILE}" up -d
down_identity:
	docker compose -f "${IDENTITY_PATH}/docker-compose.yaml" --env-file="${IDENTITY_PATH}/${ENV_FILE}" down

up_cpu_system_nano: up_identity up_cpu_recognition
down_cpu_system_nano: down_identity down_cpu_recognition
restart_cpu_system_nano: down_cpu_system_nano up_cpu_system_nano

up_cpu_system_minimal: up_identity up_cpu_recognition up_storage
down_cpu_system_minimal: down_identity down_cpu_recognition down_storage
restart_cpu_system_minimal: down_cpu_system_minimal up_cpu_system_minimal

up_cpu_system: up_identity up_cpu_recognition up_storage
down_cpu_system: down_identity down_cpu_recognition down_storage
restart_cpu_system: down_cpu_system up_cpu_system

restart_cpu_recognition: down_cpu_recognition up_cpu_recognition
