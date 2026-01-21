#!/bin/bash

docker run --rm -it \
	-p 8904:8904 \
	-v .:/project/number-plate-tests \
	number-plate-tests bash
