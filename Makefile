.PHONY: clean-root

clean-root:
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -type d -exec rm -r "{}" +
