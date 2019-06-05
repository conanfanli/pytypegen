.PHONY: clean
clean:
	@rm -rf dist pytypegen.egg-info
	@rm -rf .cover
	@rm -f .coverage

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
publish: clean
	python setup.py sdist bdist_wheel
	twine upload dist/* --config-file .pypirc --skip-existing

.PHONY: generate-stubs
generate-stubs: clean
	find . -type f -name '*.pyi' | xargs rm
	stubgen pytypegen/ -o .
	find . -type f -name '*.pyi' | xargs bin/fix_stubs.py

