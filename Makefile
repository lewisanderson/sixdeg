# Makefile

# The default target if none is specified
.PHONY: all
all: test


build:
	@docker build -t wikipull .


test: build
	@python3 -m unittest discover -s scripts -p '*_ut.py'


run: build
	@docker3 run -it --rm wikipull python3 scripts/wikipull.py

