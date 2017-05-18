.PHONY: all

all: transcrypt

.PHONY: transcrypt
transcrypt: docs/__javascript__/yapspell.js docs/__javascript__/yapspell.min.js docs/__javascript__/yapspell.mod.js

docs/__javascript__/yapspell.js docs/__javascript__/yapspell.min.js docs/__javascript__/yapspell.mod.js: yapspell.py
	transcrypt yapspell.py
	mkdir -p docs/__javascript__
	mv __javascript__/yapspell.js docs/__javascript__/yapspell.js
	mv __javascript__/yapspell.min.js docs/__javascript__/yapspell.min.js
	mv __javascript__/yapspell.mod.js docs/__javascript__/yapspell.mod.js
	rmdir __javascript__
