#!/bin/bash
# preprocess the file using gcc
# further compile it using nmlc

gcc -E -x c -o jplw.nml jplw.pnml &&
	echo "Finished preprocessing..." &&
	echo "Compiling..." &&
	nmlc jplw.nml -o jplw.grf --nml=jplw_parsed.nml &&
	echo "done!"
