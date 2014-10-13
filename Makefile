clean:
	@find . -iname '*.orig' -delete 
	@find . -iname '*.pyc' -delete
	@find . -iname '*~' -delete
	@rm -rf dist/
	@rm -rf python-wtf.egg-info
	@rm -f requirements_update.out

distclean:
	@git clean -f

test:
	@for testfile in test_*.py; do \
		echo Running tests in $$testfile...; \
		python ./$$testfile; done

#publish:
#	@ipython register.py
