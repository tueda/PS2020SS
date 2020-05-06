# Requirements: python>=3.6, poetry>=1.0

MAKEFLAGS = --no-print-directory

build:
	@poetry run make __build

__build:
	python scripts/make-links.py
	python scripts/make-footnotes.py
	python scripts/check-spell.py

install:
	poetry install
	poetry run pre-commit install
	poetry run pre-commit install --hook-type commit-msg
	poetry run jupyter nbextension enable --py widgetsnbextension

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

serve:
	poetry run mkdocs serve

deploy:
	poetry run mkdocs gh-deploy
