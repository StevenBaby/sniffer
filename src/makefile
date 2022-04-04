
ui/%.py: ui/%.ui
	PySide6-uic $< -o $@

.PHONY: ui
ui: \
	ui/main.py \
	ui/about.py \

.PHONY: clean
clean:
	rm ui/main.py
