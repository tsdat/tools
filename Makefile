build:
	rm -rf dist/
	python -m build
	pip install dist/*.whl
