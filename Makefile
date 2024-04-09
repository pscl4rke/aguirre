
pre-release-checks: | venv.testing
	venv.testing/bin/mypy aguirre
	venv.testing/bin/pyroma . || true

test:
	python3 -m unittest discover tests/

venv.testing:
	python3 -m venv $@
	$@/bin/pip install .[testing]
