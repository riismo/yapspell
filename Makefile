.PHONY: all

all: transcrypt

.PHONY: transcrypt
transcrypt: docs/yapspell.js docs/yapspell.min.js docs/yapspell.mod.js

docs/yapspell.js docs/yapspell.min.js docs/yapspell.mod.js: yapspell.py
	transcrypt yapspell.py
	mkdir -p docs/__javascript__
	mv __javascript__/yapspell.js docs/yapspell.js
	mv __javascript__/yapspell.min.js docs/yapspell.min.js
	mv __javascript__/yapspell.mod.js docs/yapspell.mod.js
	rmdir __javascript__
