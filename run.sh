#!/usr/bin/env bash

docker run --rm -it \
	-v .:/app \
	-p 8000:8000 \
	moujikov/number-plates-all
