
pre-release-checks: | venv.testing
	venv.testing/bin/mypy aguirre
	venv.testing/bin/pyroma . || true

test:
	python3 -m unittest discover tests/

venv.testing:
	python3 -m venv $@
	$@/bin/pip install .[testing]


####

release:
	test ! -d dist
	python3 setup.py sdist bdist_wheel
	ls -la dist
	check-wheel-contents dist
	twine check dist/*.whl dist/*.tar.gz
	PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring twine upload dist/*
	mv -i build* *.egg-info dist/.
	mv dist dist.$$(date +%Y%m%d.%H%M%S)

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
