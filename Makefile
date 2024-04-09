
pre-release-checks: | venv.testing
	venv.testing/bin/mypy aguirre
	venv.testing/bin/pyroma . || true

test:
	python3 -m unittest discover tests/

venv.testing:
	python3 -m venv $@
	$@/bin/pip install .[testing]


####

docker-to-run += test-in-docker-3.7-slim-bullseye
docker-to-run += test-in-docker-3.8-slim-bullseye
docker-to-run += test-in-docker-3.9-slim-bullseye
docker-to-run += test-in-docker-3.10-slim-bullseye
test-in-docker: $(docker-to-run)

test-in-docker-%:
	@echo
	@echo "===================================================="
	@echo "Testing with python:$*"
	@echo "===================================================="
	@echo
	docker run -t --rm 											\
		--entrypoint /bin/sh									\
		--workdir /root											\
		--volume .:/root:ro										\
		python:$* 												\
		-c '													\
				pwd												\
			&&	pip --no-cache-dir install .[testing]			\
			&&	mypy --cache-dir /dev/null aguirre				\
			&&	python -m unittest discover tests/				\
			&&	(pyroma . || true)								\
		'
