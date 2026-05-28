"""Makefile behavior and macro tests.

This package contains pytest tests that verify the critical guard and
delegation logic in the project's Makefile.

The tests deliberately use self-contained minimal Makefiles containing
copies of HOST_ONLY_GUARD and RUN_IN_CONTAINER so that macro regressions
can be caught quickly and independently of the full real Makefile.
"""
