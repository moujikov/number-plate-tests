#!/usr/bin/env bash

docker run --rm -it \
	-v .:/project/number-plate-tests \
	-p 8000:8000 \
	moujikov/number-plate-tests bash
