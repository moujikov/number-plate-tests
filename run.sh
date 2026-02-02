#!/usr/bin/env bash

docker run --rm -it \
	-v .:/number-plates \
	-p 8000:8000 \
	moujikov/number-plate-tests bash
