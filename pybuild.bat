@echo off
:start
py nml_compiler.py -f "jplw.pnml" -o "jplw.nml"
nmlc jplw.nml -o jplw.grf 
move /y C:\Users\Jakob\Games\GitHub\JPengines\jplw.grf C:\Users\Jakob\Games\OpenTTD-JGR-+\newgrf\jakesdevland
pause
goto start