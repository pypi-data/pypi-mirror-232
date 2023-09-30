# remove all implicit rules: easier debugging and I don't need them
.SUFFIXES:

PROJECT := runexp
VERSION := $(shell grep "version" pyproject.toml | cut -d '"' -f 2 | tr -d '\n')

PYTHON_FILES := $(shell find src/ -type f -name "*.py")

# dist files for the current version
DIST_SUFFIX = -py3-none-any.whl .tar.gz
DIST_FILES := $(addprefix dist/$(PROJECT)-$(VERSION),$(DIST_SUFFIX))

# make sure everything is OK
info:
	@echo "VERIONS: $(VERSION)"
	@echo "PY: $(PYTHON_FILES)"
	@echo "DIST: $(DIST_FILES)"


# TODO use a pattern rule to avoid the need for intermediate files
# see https://stackoverflow.com/a/3077254

%-py3-none-any.whl %.tar.gz: $(PYTHON_FILES)
	@echo "PY: $(PYTHON_FILES)"
	@echo "DIST: $(DIST_FILES)"
	. .venv/bin/activate; python -m build

build: $(DIST_FILES)

#.PHONY: upload
#upload: $(DIST_FILES)
#	@echo "uploading package"
#	. .venv/bin/activate; python -m twine upload --config-file pypi-no-test.pypirc dist/*

# remove the cached files (note the $$ to escape the patterns)
clear_caches:
	find . | grep -E "(/__pycache__$$|\.pyc$$|\.pyo$$)" | xargs rm -rf

# remove dist files
clean:
	rm -rf $(DIST_FILES)

.PHONY: info build clear_caches clean
