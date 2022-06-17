setup:
	conda env create -f environment.yml || conda env update -f environment.yml

build_pypi_package:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	python setup.py sdist bdist_wheel

twine_upload: build_pypi_package
	@twine upload \
		--repository-url https://upload.pypi.org/legacy/ \
		-u $(PYPI_USER) \
		-p $(PYPI_PASS) \
		dist/*-py3-none-any.whl