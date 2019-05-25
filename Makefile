
.PHONY: test
test:
	PYTHONPATH=. pytest $(filter-out $@,$(MAKECMDGOALS))

.PHONY: coverage
coverage: ## Generate a test coverage report based on `manage.py test`
	PYTHONPATH=. pytest . --cov=. --cov-report term-missing \
			   --cov-report html:.cover \
			   --cov-report xml:./coverage.xml \
			   --junitxml ./test-reports/xunit.xml

.PHONY: setup
setup:
	rm -rf .git/hooks && ln -s $(shell pwd)/git-hooks .git/hooks

.PHONY: publish
publish:
	rm -rf build dist
	python setup.py bdist_wheel
	twine upload dist/* --config-file .pypirc
