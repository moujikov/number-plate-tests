#!/bin/bash

docker run --rm -it \
	-v .:/project/number-plate-tests \
	number-plate-tests bash
