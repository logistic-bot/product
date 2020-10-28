default: style mypy

style: format
	flake8 --max-line-length=120 --max-doc-length=100 --show-source --statistics --jobs 4 --doctests src main.py --ignore=E261,W503
	pylint src main.py -f colorized --ignore-patterns='test*' --disable=C0330,R0913,W1116,R0903,W0511,R0914,E1111,R0801,R0902,R0201,C0103,W0707 --max-line-length=120
	@make radon

radon:
	radon mi main.py src --sort --show --min B
	radon cc main.py src --show-complexity --min C

format:
	black .

mypy:
	mypy main.py --strict --show-error-context --pretty

coverage:
	@pytest --cov=src --ff --nf tests --durations=2 --cov-report term-missing:skip-covered -x

run:
	python main.py
	stty sane
