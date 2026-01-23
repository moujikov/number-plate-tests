#!/bin/bash

docker run --rm -it \
	-v .:/project/number-plate-tests \
	moujikov/number-plate-tests bash
