@echo off
:start
py nml_compiler.py -f "jplw.pnml" -o "jplw.nml"
nmlc jplw.nml -o jplw.grf 
pause
goto start