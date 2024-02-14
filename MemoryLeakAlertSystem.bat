@echo off
set "projpath=C:\MyProj\EclipseMATAutoEmail"
set "reportpath=\MATReports"
set "filename=\batch_test.hprof"
set "jcmdpath=%projpath%%reportpath%%filename%"
jcmd "%1" "GC.heap_dump" "%jcmdpath%"
python "C:\MyProj\EclipseMATAutoEmail\HPROFAnalyzer.py" "%filename%" "%2" "%3" "%4"
