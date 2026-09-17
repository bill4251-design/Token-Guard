# Contributing

Thanks for improving Token Guard. Please keep changes local-first, dependency-light, and covered by tests.

1. Create a branch and install with `pip install -e .`.
2. Run `python -m unittest discover -s tests -v` before opening a pull request.
3. Add a focused test for each behaviour change and do not commit databases, prompts, keys, or generated reports.
4. Describe provider-specific assumptions in the pull request.
