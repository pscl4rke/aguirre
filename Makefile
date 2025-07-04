
testdir := tests

pre-release-checks: | venv.testing
	venv.testing/bin/mypy aguirre
	venv.testing/bin/pyroma . || true

test: | venv.testing
	venv.testing/bin/coverage run -m unittest discover $(testdir)
	venv.testing/bin/coverage report -m

venv.testing:
	python3 -m venv $@
	$@/bin/pip install -e '.[testing]'


####

release: export PYTHON_KEYRING_BACKEND := keyring.backends.null.Keyring
release:
	test '$(shell python3 setup.py --version)' = '$(shell git describe)'
	test ! -d dist
	python3 setup.py sdist bdist_wheel
	check-wheel-contents dist
	twine check dist/*
	twine upload dist/*
	mv -i build* *.egg-info dist/.
	mv dist dist.$$(date +%Y-%m-%d.%H%M%S)

####

docker-to-run += test-in-docker-3.7-slim-bullseye
docker-to-run += test-in-docker-3.8-slim-bullseye
docker-to-run += test-in-docker-3.9-slim-bullseye
docker-to-run += test-in-docker-3.10-slim-bullseye
docker-to-run += test-in-docker-3.11-slim-bullseye
docker-to-run += test-in-docker-3.12-slim-bookworm

test-in-docker: $(docker-to-run)

test-in-docker-%:
	@echo
	@echo "=============================================================="
	@echo "Testing with docker.io/library/python:$*"
	@echo "=============================================================="
	@echo
	ephemerun \
		-i "docker.io/library/python:$*" \
		-v "`pwd`:/root/src:ro" \
		-W "/root" \
		-S "cp -air ./src/* ." \
		-S "pip --no-cache-dir install .[testing]" \
		-S "mypy --cache-dir /dev/null aguirre" \
		-S "coverage run -m unittest discover $(testdir)" \
		-S "coverage report -m" \
		-S "(pyroma . || true)"
