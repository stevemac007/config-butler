configure:
	pip install .
	pip install coverage
	pip install coveralls
	pip install flake8

lint:
	flake8 configbutler --ignore E501,E722

test:
	python setup.py test

test.py2:
	python2 setup.py test

coverage:
	coverage run --source=configbutler/ setup.py test
	coverage report