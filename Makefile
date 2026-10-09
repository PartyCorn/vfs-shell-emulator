PYTHON ?= python3

.PHONY: run test demo

run:
	$(PYTHON) src/main.py

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -v

demo:
	for s in scripts/stage*.sh; do echo "== $$s"; sh $$s; done
