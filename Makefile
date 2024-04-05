
pre-release-checks:
	mypy aguirre
	pyroma .

test:
	python3 -m unittest discover tests/
