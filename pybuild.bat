@echo off
:start
gcc -E -x c -o JPengines.nml jplw.pnml
nmlc -c JPengines.nml -o "D:\DocumentsWin\OpenTTD\newgrf\JPengines.grf" -o JPengines.grf -t custom_tags.txt
pause
goto start