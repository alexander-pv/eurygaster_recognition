
.PHONY: load_test_req
load_test_req:
	pip install -r ./inference/tests/locustfiles/requirements.txt

.PHONY: load_test
load_test: load_test_req
	locust

.PHONY: bento_test
bento_test:
	cd inference && \
	pip install -r requirements_test.txt && \
	pytest --verbosity=1 -s
