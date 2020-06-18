# Requirements: python>=3.6, poetry>=1.0 and GNU make

MAKEFLAGS = --no-print-directory
export JUPYTER_CONFIG_DIR = .jupyter

build:
	@poetry run make __build

__build:
	python scripts/make-links.py
	python scripts/make-footnotes.py
	python scripts/check-spell.py

install:
	@poetry run make __install

__install:
	poetry install
	pre-commit install
	pre-commit install --hook-type commit-msg
	jupyter nbextension enable --py widgetsnbextension --sys-prefix
	jupyter labextension install @jupyter-widgets/jupyterlab-manager

fmt:
	@poetry run make __fmt

__fmt:
	black .
	reorder-python-imports --exit-zero-even-if-changed scripts/*.py

lint:
	@poetry run make __lint

__lint:  __fmt
	flake8
	mypy scripts

notebook:
	poetry run jupyter notebook --no-browser

lab:
	poetry run jupyter lab --no-browser

serve:
	poetry run mkdocs serve

deploy:
	poetry run mkdocs gh-deploy

viewer:
ifdef CLIPBOARD
	poetry run python scripts/viewer.py --clipboard
else
	poetry run python scripts/viewer.py
endif
